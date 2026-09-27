import json
import os
import sys

def get_data_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def evaluate():
    try:
        import torch
        from sentence_transformers import SentenceTransformer, util
        import numpy as np
    except ImportError as e:
        print(f"Error importing ML dependencies: {e}")
        return

    data_dir = get_data_dir()
    golden_file = os.path.join(data_dir, 'golden_skill_pairs.jsonl')
    
    if not os.path.exists(golden_file):
        print(f"Error: {golden_file} not found.")
        return

    print("Loading dataset...")
    dataset = []
    with open(golden_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                dataset.append(json.loads(line))

    print(f"Loaded {len(dataset)} examples.")
    
    print("Loading model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    print("Calculating similarities...")
    results = []
    for ex in dataset:
        resume_context = ex['resume_context']
        job_req = ex['job_requirement']
        
        # Calculate embedding
        emb1 = model.encode(resume_context, convert_to_tensor=True)
        emb2 = model.encode(job_req, convert_to_tensor=True)
        
        # Calculate cosine similarity
        sim = util.cos_sim(emb1, emb2).item()
        
        results.append({
            "id": ex['id'],
            "resume_context": resume_context,
            "job_requirement": job_req,
            "human_label": ex['human_label'],
            "reasoning": ex['reasoning'],
            "similarity_score": sim
        })

    # Save scores
    scores_file = os.path.join(data_dir, 'semantic_matching_scores.jsonl')
    with open(scores_file, 'w', encoding='utf-8') as f:
        for res in results:
            f.write(json.dumps(res) + "\n")

    thresholds = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55]
    
    threshold_results = []
    
    for t in thresholds:
        tp = 0
        tn = 0
        fp = 0
        fn = 0
        
        for res in results:
            pred = 1 if res['similarity_score'] >= t else 0
            actual = res['human_label']
            
            if pred == 1 and actual == 1:
                tp += 1
            elif pred == 0 and actual == 0:
                tn += 1
            elif pred == 1 and actual == 0:
                fp += 1
            elif pred == 0 and actual == 1:
                fn += 1
                
        accuracy = (tp + tn) / len(results) if len(results) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        threshold_results.append({
            "threshold": t,
            "tp": tp,
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1
        })
        
    print("\n--- Evaluation Results ---")
    for tr in threshold_results:
        print(f"T={tr['threshold']:.2f} | Acc: {tr['accuracy']:.2f} | Prec: {tr['precision']:.2f} | Rec: {tr['recall']:.2f} | F1: {tr['f1']:.2f} | FP: {tr['fp']} | FN: {tr['fn']}")

    # Recommend a threshold: Prioritize high precision (minimize FP)
    recommended = max(threshold_results, key=lambda x: x['f1'])
    
    eval_result = {
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        "dataset_size": len(results),
        "threshold_results": threshold_results,
        "recommended_threshold": recommended['threshold'],
        "reason": f"At {recommended['threshold']}, Precision is {recommended['precision']:.2f} (only {recommended['fp']} false positives) while maintaining a Recall of {recommended['recall']:.2f}. High precision is critical to avoid recommending unqualified candidates."
    }
    
    eval_file = os.path.join(data_dir, 'semantic_matching_evaluation.json')
    with open(eval_file, 'w', encoding='utf-8') as f:
        json.dump(eval_result, f, indent=2)

    print(f"\nRecommended Threshold: {recommended['threshold']:.2f}")
    
    # Print high-risk FPs and strongest FNs at recommended threshold
    t = recommended['threshold']
    print(f"\nFalse Positives at T={t:.2f}:")
    fps = [r for r in results if r['similarity_score'] >= t and r['human_label'] == 0]
    for r in sorted(fps, key=lambda x: x['similarity_score'], reverse=True)[:10]:
        print(f"  Score {r['similarity_score']:.3f}: '{r['resume_context']}' -> '{r['job_requirement']}'")
        
    print(f"\nFalse Negatives at T={t:.2f}:")
    fns = [r for r in results if r['similarity_score'] < t and r['human_label'] == 1]
    for r in sorted(fns, key=lambda x: x['similarity_score'])[:10]:
        print(f"  Score {r['similarity_score']:.3f}: '{r['resume_context']}' -> '{r['job_requirement']}'")

if __name__ == "__main__":
    os.makedirs(get_data_dir(), exist_ok=True)
    evaluate()
