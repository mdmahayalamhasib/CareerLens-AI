import json
import os
import sys

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

def simulate_rule_based(job_req, resume_ctx):
    # A tiny mock rule-based matcher that checks if exact keyword exists
    # Just used to simulate the O(1) matching philosophy
    req_norm = job_req.lower().replace('.', '')
    ctx_norm = resume_ctx.lower().replace('.', '')
    
    # Extract core keyword from job req roughly
    keywords = [w for w in req_norm.split() if len(w) > 3]
    
    match = False
    matched_word = None
    for kw in keywords:
        if kw in ctx_norm:
            match = True
            matched_word = kw
            break
            
    return {
        "explicit_skill_match": match,
        "matched_keyword": matched_word if match else "MISSING"
    }

def main():
    data_dir = get_data_dir()
    test_file = os.path.join(data_dir, 'resume_job_relevance_test.jsonl')
    
    if not os.path.exists(test_file):
        print(f"Error: {test_file} not found.")
        sys.exit(1)

    print("Loading ML model...")
    from ml.relevance_api import analyze_relevance
    
    print("Loading test dataset...")
    test_data = []
    with open(test_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                test_data.append(json.loads(line))

    # Evaluate Test Dataset
    print("\nEvaluating Test Set...")
    predictions = []
    labels = []
    
    cat_stats = {
        "direct_relevance": {"total": 0, "correct": 0, "errors": []},
        "transferable_relevance": {"total": 0, "correct": 0, "errors": []},
        "lexical_trap": {"total": 0, "correct": 0, "errors": []},
        "irrelevant": {"total": 0, "correct": 0, "errors": []},
    }
    
    test_results = []
    
    for ex in test_data:
        cat = ex['category']
        lbl = ex['label']
        
        # ML Interpretation
        ml_res = analyze_relevance(ex['job_requirement'], ex['resume_context'])
        pred = 1 if ml_res['is_relevant'] else 0
        
        predictions.append(pred)
        labels.append(lbl)
        
        cat_stats[cat]["total"] += 1
        if pred == lbl:
            cat_stats[cat]["correct"] += 1
        else:
            cat_stats[cat]["errors"].append({
                "id": ex['id'],
                "label": lbl,
                "prediction": pred,
                "score": ml_res['relevance_score'],
                "job": ex['job_requirement'],
                "resume": ex['resume_context']
            })
            
        test_results.append({
            "id": ex['id'],
            "category": cat,
            "label": lbl,
            "ml_prediction": pred,
            "ml_score": ml_res['relevance_score']
        })

    metrics = calculate_metrics(predictions, labels)

    # Specific Examples
    print("\nRunning specific shadow simulation examples...")
    
    simulations = [
        {
            "id": "sim_1",
            "type": "direct_relevance",
            "job_requirement": "REST API development",
            "resume_context": "Built a FastAPI backend with HTTP endpoints and REST APIs."
        },
        {
            "id": "sim_2",
            "type": "lexical_trap",
            "job_requirement": "Kubernetes",
            "resume_context": "Containerized applications using Docker."
        },
        {
            "id": "sim_3",
            "type": "transferable_relevance",
            "job_requirement": "React",
            "resume_context": "Built responsive interfaces using JavaScript and modern frontend frameworks."
        },
        {
            "id": "sim_4",
            "type": "transferable_relevance",
            "job_requirement": "PostgreSQL",
            "resume_context": "Designed relational databases and wrote complex SQL queries using MySQL."
        },
        {
            "id": "sim_5",
            "type": "transferable_relevance",
            "job_requirement": "Machine Learning",
            "resume_context": "Trained classification models using Python, scikit-learn and TF-IDF."
        }
    ]
    
    simulation_results = []
    
    for sim in simulations:
        rule_res = simulate_rule_based(sim['job_requirement'], sim['resume_context'])
        ml_res = analyze_relevance(sim['job_requirement'], sim['resume_context'])
        
        simulation_results.append({
            "id": sim['id'],
            "scenario": sim['type'],
            "job_requirement": sim['job_requirement'],
            "resume_context": sim['resume_context'],
            "rule_based_interpretation": rule_res,
            "ml_interpretation": ml_res
        })
        
    output = {
        "test_metrics": metrics,
        "category_metrics": cat_stats,
        "simulation_results": simulation_results
    }
    
    out_file = os.path.join(data_dir, 'relevance_shadow_evaluation.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
        
    print("\n=== SHADOW EVALUATION REPORT ===")
    print(f"Accuracy:  {metrics['accuracy']:.3f}")
    print(f"Precision: {metrics['precision']:.3f}")
    print(f"Recall:    {metrics['recall']:.3f}")
    print(f"F1 Score:  {metrics['f1']:.3f}")
    print(f"FP: {metrics['fp']} | FN: {metrics['fn']}")
    
    print("\n--- Category Errors ---")
    for cat, stats in cat_stats.items():
        errs = len(stats['errors'])
        print(f"[{cat}] Errors: {errs} / {stats['total']}")
        for e in stats['errors']:
            print(f"   -> Pred: {e['prediction']} (Score: {e['score']:.3f}) | Label: {e['label']}")
            print(f"      Job: {e['job']}")
            print(f"      Res: {e['resume']}")
            
    print("\n--- Shadow Simulations ---")
    for r in simulation_results:
        print(f"\nScenario: {r['scenario']}")
        print(f"Job: {r['job_requirement']}")
        print(f"Res: {r['resume_context']}")
        print(f"  Rule-Based Match: {r['rule_based_interpretation']['explicit_skill_match']} ({r['rule_based_interpretation']['matched_keyword']})")
        print(f"  ML Relevance:     {r['ml_interpretation']['is_relevant']} (Score: {r['ml_interpretation']['relevance_score']:.3f})")

if __name__ == "__main__":
    main()
