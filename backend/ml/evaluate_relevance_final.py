import json
import os
import torch
import sys
from sentence_transformers import SentenceTransformer, util

def get_data_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def calculate_metrics(predictions, labels):
    tp, tn, fp, fn = 0, 0, 0, 0
    for p, a in zip(predictions, labels):
        if p == 1 and a == 1: tp += 1
        elif p == 0 and a == 0: tn += 1
        elif p == 1 and a == 0: fp += 1
        elif p == 0 and a == 1: fn += 1
        
    acc = (tp + tn) / len(predictions) if len(predictions) > 0 else 0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0
    
    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn
    }

def main():
    data_dir = get_data_dir()
    test_file = os.path.join(data_dir, 'resume_job_relevance_test.jsonl')
    
    if not os.path.exists(test_file):
        print(f"Error: {test_file} not found.")
        sys.exit(1)

    print("Loading test dataset...")
    test_data = []
    with open(test_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                test_data.append(json.loads(line))
                
    if len(test_data) != 30:
        print(f"Warning: Expected 30 test examples, found {len(test_data)}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 1. Evaluate PRETRAINED model
    print("\nLoading PRETRAINED model...")
    pretrained_model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2").to(device)
    pretrained_threshold = 0.25
    pretrained_results = []
    
    for ex in test_data:
        emb1 = pretrained_model.encode(ex['resume_context'], convert_to_tensor=True, device=device)
        emb2 = pretrained_model.encode(ex['job_requirement'], convert_to_tensor=True, device=device)
        sim = util.cos_sim(emb1, emb2).item()
        pred = 1 if sim >= pretrained_threshold else 0
        pretrained_results.append({"sim": sim, "pred": pred})

    # 2. Evaluate FINETUNED model
    print("\nLoading FINETUNED model...")
    finetuned_path = os.path.join(os.path.dirname(data_dir), 'ml', 'models', 'mpnet_relevance_finetuned')
    if not os.path.exists(finetuned_path):
        print(f"Error: Fine-tuned model not found at {finetuned_path}")
        sys.exit(1)
        
    finetuned_model = SentenceTransformer(finetuned_path).to(device)
    finetuned_threshold = 0.50
    finetuned_results = []
    
    for ex in test_data:
        emb1 = finetuned_model.encode(ex['resume_context'], convert_to_tensor=True, device=device)
        emb2 = finetuned_model.encode(ex['job_requirement'], convert_to_tensor=True, device=device)
        sim = util.cos_sim(emb1, emb2).item()
        pred = 1 if sim >= finetuned_threshold else 0
        finetuned_results.append({"sim": sim, "pred": pred})
        
    # Calculate Metrics
    labels = [ex['label'] for ex in test_data]
    pt_preds = [r['pred'] for r in pretrained_results]
    ft_preds = [r['pred'] for r in finetuned_results]
    
    pt_metrics = calculate_metrics(pt_preds, labels)
    ft_metrics = calculate_metrics(ft_preds, labels)
    
    # Save per-example scores
    scores_file = os.path.join(data_dir, 'relevance_final_test_scores.jsonl')
    with open(scores_file, 'w', encoding='utf-8') as f:
        for i, ex in enumerate(test_data):
            res_obj = {
                "id": ex['id'],
                "category": ex['category'],
                "label": ex['label'],
                "job_requirement": ex['job_requirement'],
                "resume_context": ex['resume_context'],
                "reason": ex['reason'],
                "pretrained_score": pretrained_results[i]['sim'],
                "pretrained_prediction": pretrained_results[i]['pred'],
                "finetuned_score": finetuned_results[i]['sim'],
                "finetuned_prediction": finetuned_results[i]['pred']
            }
            f.write(json.dumps(res_obj) + "\n")
            
    # Category Analysis for Fine-tuned model
    cat_analysis = {}
    ft_errors = []
    for i, ex in enumerate(test_data):
        cat = ex['category']
        if cat not in cat_analysis:
            cat_analysis[cat] = {"total": 0, "correct": 0, "incorrect": 0, "fp": 0, "fn": 0}
            
        cat_analysis[cat]["total"] += 1
        
        pred = finetuned_results[i]['pred']
        actual = ex['label']
        
        if pred == actual:
            cat_analysis[cat]["correct"] += 1
        else:
            cat_analysis[cat]["incorrect"] += 1
            if pred == 1 and actual == 0:
                cat_analysis[cat]["fp"] += 1
            elif pred == 0 and actual == 1:
                cat_analysis[cat]["fn"] += 1
                
            ft_errors.append({
                "id": ex['id'],
                "category": cat,
                "label": actual,
                "prediction": pred,
                "model_score": finetuned_results[i]['sim'],
                "job_requirement": ex['job_requirement'],
                "resume_context": ex['resume_context'],
                "original_reason": ex['reason']
            })

    # Summary Report
    improvement = {
        "accuracy_change": ft_metrics['accuracy'] - pt_metrics['accuracy'],
        "precision_change": ft_metrics['precision'] - pt_metrics['precision'],
        "recall_change": ft_metrics['recall'] - pt_metrics['recall'],
        "f1_change": ft_metrics['f1'] - pt_metrics['f1'],
        "fp_change": ft_metrics['fp'] - pt_metrics['fp'],
        "fn_change": ft_metrics['fn'] - pt_metrics['fn']
    }
    
    summary = {
        "test_count": len(test_data),
        "pretrained": {
            "threshold": pretrained_threshold,
            **pt_metrics
        },
        "finetuned": {
            "threshold": finetuned_threshold,
            **ft_metrics,
            "category_analysis": cat_analysis,
            "errors": ft_errors
        },
        "improvement": improvement
    }
    
    results_file = os.path.join(data_dir, 'relevance_final_test_results.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
        
    print("\n=== FINAL TEST EVALUATION ===")
    print(f"Test Count: {len(test_data)}")
    
    print("\n| Model | Threshold | Accuracy | Precision | Recall | F1 | FP | FN |")
    print("|-------|-----------|----------|-----------|--------|----|----|----|")
    print(f"| Pretrained | {pretrained_threshold:.2f} | {pt_metrics['accuracy']:.3f} | {pt_metrics['precision']:.3f} | {pt_metrics['recall']:.3f} | {pt_metrics['f1']:.3f} | {pt_metrics['fp']} | {pt_metrics['fn']} |")
    print(f"| Finetuned  | {finetuned_threshold:.2f} | {ft_metrics['accuracy']:.3f} | {ft_metrics['precision']:.3f} | {ft_metrics['recall']:.3f} | {ft_metrics['f1']:.3f} | {ft_metrics['fp']} | {ft_metrics['fn']} |")
    
    print("\n--- Exact Metric Changes ---")
    for k, v in improvement.items():
        sign = "+" if v > 0 else ""
        print(f"  {k}: {sign}{v:.3f}")
        
    print("\n--- Category-Level Results (Fine-tuned Model) ---")
    for cat, stats in cat_analysis.items():
        print(f"  [{cat}] Total: {stats['total']} | Correct: {stats['correct']} | Incorrect: {stats['incorrect']} | FP: {stats['fp']} | FN: {stats['fn']}")
        
    print("\n--- All Errors (Fine-tuned Model) ---")
    if not ft_errors:
        print("  ZERO errors. The model predicted all test examples perfectly.")
    else:
        for err in ft_errors:
            print(f"  ID: {err['id']} | Cat: {err['category']} | Lbl: {err['label']} | Pred: {err['prediction']} | Score: {err['model_score']:.3f}")
            print(f"    Job: {err['job_requirement']}")
            print(f"    Res: {err['resume_context']}")
            print(f"    Rsn: {err['original_reason']}")

if __name__ == "__main__":
    main()
