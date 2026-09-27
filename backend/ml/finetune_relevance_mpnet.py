import json
import os
import torch
import random
import sys
import numpy as np
import copy
from torch.utils.data import DataLoader
from torch.optim import AdamW
from sentence_transformers import SentenceTransformer, InputExample, util
from sentence_transformers import losses

def get_data_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def main():
    set_seed(42)
    
    data_dir = get_data_dir()
    train_file = os.path.join(data_dir, 'resume_job_relevance_train.jsonl')
    val_file = os.path.join(data_dir, 'resume_job_relevance_validation.jsonl')
    
    if not os.path.exists(train_file) or not os.path.exists(val_file):
        print("Error: Train or validation file not found.")
        sys.exit(1)
        
    print("Loading data...")
    train_data = []
    with open(train_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                train_data.append(json.loads(line))
                
    val_data = []
    with open(val_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                val_data.append(json.loads(line))
                
    print(f"Loaded {len(train_data)} train examples and {len(val_data)} validation examples.")
    
    train_examples = []
    for ex in train_data:
        train_examples.append(InputExample(texts=[ex['job_requirement'], ex['resume_context']], label=float(ex['label'])))
        
    model_name = "sentence-transformers/all-mpnet-base-v2"
    print(f"Loading pretrained model: {model_name}")
    try:
        model = SentenceTransformer(model_name)
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)
        
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    model.to(device)

    # Use sentence-transformers custom collate function for InputExamples
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=8, collate_fn=model.smart_batching_collate)
    
    # Standard CosineSimilarityLoss wraps the model
    train_loss = losses.CosineSimilarityLoss(model).to(device)
    
    epochs = 3
    learning_rate = 2e-5
    weight_decay = 0.01
    
    optimizer = AdamW(train_loss.parameters(), lr=learning_rate, weight_decay=weight_decay)
    
    print(f"Training for {epochs} epochs...")
    
    best_f1 = -1
    best_threshold = None
    best_metrics = None
    best_epoch = -1
    best_model_state = None
    
    thresholds = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]

    for epoch in range(1, epochs + 1):
        print(f"\n--- Epoch {epoch}/{epochs} ---")
        model.train()
        train_loss.train()
        total_loss = 0
        
        for batch in train_dataloader:
            features, labels = batch
            # Move to device
            features = [{k: (v.to(device) if isinstance(v, torch.Tensor) else v) for k, v in f.items()} for f in features]
            labels = labels.to(device)
            
            optimizer.zero_grad()
            loss = train_loss(features, labels)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        print(f"Epoch {epoch} loss: {total_loss/len(train_dataloader):.4f}")
        
        # Validation evaluation
        model.eval()
        with torch.no_grad():
            model_results = []
            for ex in val_data:
                emb1 = model.encode(ex['resume_context'], convert_to_tensor=True, device=device)
                emb2 = model.encode(ex['job_requirement'], convert_to_tensor=True, device=device)
                sim = util.cos_sim(emb1, emb2).item()
                model_results.append({"sim": sim, "label": ex['label']})
                
            # Find best F1 for this epoch
            epoch_best_f1 = -1
            epoch_best_t = None
            epoch_best_metrics = None
            
            for t in thresholds:
                tp, tn, fp, fn = 0, 0, 0, 0
                for res in model_results:
                    pred = 1 if res['sim'] >= t else 0
                    actual = res['label']
                    if pred == 1 and actual == 1: tp += 1
                    elif pred == 0 and actual == 0: tn += 1
                    elif pred == 1 and actual == 0: fp += 1
                    elif pred == 0 and actual == 1: fn += 1
                        
                accuracy = (tp + tn) / len(model_results) if len(model_results) > 0 else 0
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                
                t_metrics = {
                    "threshold": t,
                    "accuracy": accuracy,
                    "precision": precision,
                    "recall": recall,
                    "f1": f1,
                    "tp": tp,
                    "tn": tn,
                    "fp": fp,
                    "fn": fn
                }
                if f1 > epoch_best_f1:
                    epoch_best_f1 = f1
                    epoch_best_t = t
                    epoch_best_metrics = t_metrics
                    
            print(f"Validation F1: {epoch_best_f1:.3f} at T={epoch_best_t}")
            
            # Save if this is the best epoch overall
            if epoch_best_f1 > best_f1:
                best_f1 = epoch_best_f1
                best_threshold = epoch_best_t
                best_metrics = epoch_best_metrics
                best_epoch = epoch
                # we don't save to disk on every epoch to save time, just keep state dict in RAM
                best_model_state = copy.deepcopy(model.state_dict())
                
    print(f"\n--- Sweeping Completed ---")
    print(f"Best overall Validation F1: {best_f1:.3f} at T={best_threshold} (Epoch {best_epoch})")
    
    # Save best model to disk
    best_model_path = os.path.join(os.path.dirname(data_dir), 'ml', 'models', 'mpnet_relevance_finetuned')
    os.makedirs(best_model_path, exist_ok=True)
    
    # Restore best weights and save
    model.load_state_dict(best_model_state)
    model.save(best_model_path)
    print(f"Saved best model to {best_model_path}")
    
    val_report_path = os.path.join(data_dir, 'relevance_finetuning_validation.json')
    val_report = {
        "model": "mpnet_relevance_finetuned",
        "base_model": model_name,
        "seed": 42,
        "training_examples": len(train_data),
        "validation_examples": len(val_data),
        "best_epoch": best_epoch,
        "best_threshold": best_threshold,
        "accuracy": best_metrics['accuracy'],
        "precision": best_metrics['precision'],
        "recall": best_metrics['recall'],
        "f1": best_metrics['f1'],
        "tp": best_metrics['tp'],
        "tn": best_metrics['tn'],
        "fp": best_metrics['fp'],
        "fn": best_metrics['fn']
    }
    
    with open(val_report_path, 'w', encoding='utf-8') as f:
        json.dump(val_report, f, indent=2)
        
    print("\n--- FINAL REPORT ---")
    print(f"Best Validation Epoch: {best_epoch}")
    print(f"Validation Threshold: {best_threshold}")
    print(f"Validation Accuracy:  {best_metrics['accuracy']:.3f}")
    print(f"Validation Precision: {best_metrics['precision']:.3f}")
    print(f"Validation Recall:    {best_metrics['recall']:.3f}")
    print(f"Validation F1:        {best_metrics['f1']:.3f}")
    print(f"Validation FP:        {best_metrics['fp']}")
    print(f"Validation FN:        {best_metrics['fn']}")
    print(f"Test Set Accessed:    False")

if __name__ == "__main__":
    main()
