import json
import os
import sys
import traceback

def get_data_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def main():
    try:
        import torch
        from sentence_transformers import SentenceTransformer, util
        import numpy as np
    except ImportError as e:
        print(f"Error importing ML dependencies: {e}")
        sys.exit(1)

    data_dir = get_data_dir()
    golden_file = os.path.join(data_dir, 'resume_job_relevance_golden.jsonl')
    
    if not os.path.exists(golden_file):
        print(f"Error: {golden_file} not found.")
        sys.exit(1)

    print("Loading dataset...")
    dataset = []
    with open(golden_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                dataset.append(json.loads(line))

    print(f"Loaded {len(dataset)} examples.")

    models_to_test = [
        "sentence-transformers/all-MiniLM-L6-v2",
        "sentence-transformers/all-mpnet-base-v2",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ]

    thresholds = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80]
    
    scores_file = os.path.join(data_dir, 'relevance_model_scores.jsonl')
    evaluation_file = os.path.join(data_dir, 'relevance_model_evaluation.json')
    
    # clear previous scores
    with open(scores_file, 'w', encoding='utf-8') as f:
        pass

    all_evaluations = {}

    for model_name in models_to_test:
        print(f"\n--- Testing model: {model_name} ---")
        try:
            model = SentenceTransformer(model_name)
        except Exception as e:
            print(f"Failed to load model {model_name}: {e}")
            traceback.print_exc()
            continue
            
        model_results = []
        for ex in dataset:
            resume_context = ex['resume_context']
            job_req = ex['job_requirement']
            
            # Calculate embedding
            emb1 = model.encode(resume_context, convert_to_tensor=True)
            emb2 = model.encode(job_req, convert_to_tensor=True)
            
            # Calculate cosine similarity
            sim = util.cos_sim(emb1, emb2).item()
            
            res_obj = {
                "id": ex['id'],
                "model": model_name,
                "similarity": sim,
                "label": ex['label'],
                "job_requirement": job_req,
                "resume_context": resume_context
            }
            model_results.append(res_obj)
            
            with open(scores_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(res_obj) + "\n")

        threshold_results = []
        best_f1 = -1
        best_threshold = None
        best_metrics = None
        
        for t in thresholds:
            tp, tn, fp, fn = 0, 0, 0, 0
            
            for res in model_results:
                pred = 1 if res['similarity'] >= t else 0
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
            threshold_results.append(t_metrics)
            
            if f1 > best_f1:
                best_f1 = f1
                best_threshold = t
                best_metrics = t_metrics

        all_evaluations[model_name] = {
            "threshold_results": threshold_results,
            "best_f1_threshold": best_threshold,
            "best_f1_metrics": best_metrics
        }
        print(f"Completed {model_name}. Best F1: {best_f1:.3f} at T={best_threshold}")

    with open(evaluation_file, 'w', encoding='utf-8') as f:
        json.dump(all_evaluations, f, indent=2)
        
    print("\n\n=== FINAL SUMMARY ===")
    
    best_overall_model = None
    best_overall_f1 = -1
    
    for model_name, evals in all_evaluations.items():
        best_metrics = evals['best_f1_metrics']
        print(f"\nModel: {model_name}")
        print(f"Best Threshold (F1): {best_metrics['threshold']:.2f}")
        print(f"  Acc:  {best_metrics['accuracy']:.3f}")
        print(f"  Prec: {best_metrics['precision']:.3f}")
        print(f"  Rec:  {best_metrics['recall']:.3f}")
        print(f"  F1:   {best_metrics['f1']:.3f}")
        print(f"  FP:   {best_metrics['fp']}")
        print(f"  FN:   {best_metrics['fn']}")
        
        if best_metrics['f1'] > best_overall_f1:
            best_overall_f1 = best_metrics['f1']
            best_overall_model = model_name

    print(f"\n--- Top Errors for Best Model ({best_overall_model}) ---")
    best_eval = all_evaluations[best_overall_model]['best_f1_metrics']
    best_t = best_eval['threshold']
    
    # Reload scores to find FPs and FNs
    all_scores = []
    with open(scores_file, 'r', encoding='utf-8') as f:
        for line in f:
            all_scores.append(json.loads(line))
            
    best_model_scores = [x for x in all_scores if x['model'] == best_overall_model]
    
    fps = [x for x in best_model_scores if x['similarity'] >= best_t and x['label'] == 0]
    fns = [x for x in best_model_scores if x['similarity'] < best_t and x['label'] == 1]
    
    fps.sort(key=lambda x: x['similarity'], reverse=True)
    fns.sort(key=lambda x: x['similarity'])
    
    print("\nTop False Positives (Highest similarity, but label=0):")
    for fp in fps[:10]:
        print(f"  Score {fp['similarity']:.3f} | Job: '{fp['job_requirement']}'")
        print(f"                  | Res: '{fp['resume_context']}'")
        
    print("\nTop False Negatives (Lowest similarity, but label=1):")
    for fn in fns[:10]:
        print(f"  Score {fn['similarity']:.3f} | Job: '{fn['job_requirement']}'")
        print(f"                  | Res: '{fn['resume_context']}'")

if __name__ == '__main__':
    main()
