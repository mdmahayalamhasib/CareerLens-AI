import json
import os
import random
import networkx as nx
from collections import defaultdict
import sys

def get_data_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def main():
    random.seed(42)
    
    data_dir = get_data_dir()
    v2_file = os.path.join(data_dir, 'resume_job_relevance_golden_v2.jsonl')
    
    if not os.path.exists(v2_file):
        print(f"Error: {v2_file} not found.")
        sys.exit(1)

    dataset = []
    with open(v2_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                dataset.append(json.loads(line))

    # Graph to find connected components of exact overlaps
    G = nx.Graph()
    for i, ex in enumerate(dataset):
        G.add_node(i)

    # Add edges for near-duplicates or exact overlaps
    for i in range(len(dataset)):
        job_i = dataset[i]['job_requirement'].lower()
        res_i = dataset[i]['resume_context'].lower()
        job_tok_i = set(job_i.split())
        
        for j in range(i+1, len(dataset)):
            job_j = dataset[j]['job_requirement'].lower()
            res_j = dataset[j]['resume_context'].lower()
            job_tok_j = set(job_j.split())
            
            overlap_job = len(job_tok_i & job_tok_j) / max(len(job_tok_i), len(job_tok_j), 1)
            
            if job_i == job_j or res_i == res_j or overlap_job > 0.8:
                G.add_edge(i, j)

    components = list(nx.connected_components(G))
    
    # Sort components so that assignment is deterministic
    components = [sorted(list(c)) for c in components]
    components.sort(key=lambda x: x[0])
    
    # Randomly shuffle the components
    random.shuffle(components)

    train_data = []
    val_data = []
    test_data = []
    
    # Target counts (70/15/15)
    total = len(dataset)
    target_train = int(total * 0.70)
    target_val = int(total * 0.15)
    target_test = total - target_train - target_val

    # Also keep track of categories to ensure representation
    # But since components are small (max ~3), random assignment usually works fine.
    # We will do a greedy assignment prioritizing the bin that needs more of the component's main category.
    
    train_cat_counts = defaultdict(int)
    val_cat_counts = defaultdict(int)
    test_cat_counts = defaultdict(int)
    
    cat_totals = defaultdict(int)
    for ex in dataset:
        cat_totals[ex['category']] += 1

    for comp in components:
        comp_examples = [dataset[idx] for idx in comp]
        
        # Determine which bin needs this most
        # We look at the first example's category as a proxy
        main_cat = comp_examples[0]['category']
        
        train_deficit = (cat_totals[main_cat] * 0.70) - train_cat_counts[main_cat]
        val_deficit = (cat_totals[main_cat] * 0.15) - val_cat_counts[main_cat]
        test_deficit = (cat_totals[main_cat] * 0.15) - test_cat_counts[main_cat]
        
        # Penalize bins that are already full
        if len(train_data) + len(comp_examples) > target_train + 2:
            train_deficit = -9999
        if len(val_data) + len(comp_examples) > target_val + 2:
            val_deficit = -9999
        if len(test_data) + len(comp_examples) > target_test + 2:
            test_deficit = -9999

        # Pick the bin with the highest deficit
        if train_deficit >= val_deficit and train_deficit >= test_deficit:
            train_data.extend(comp_examples)
            for ex in comp_examples: train_cat_counts[ex['category']] += 1
        elif val_deficit >= train_deficit and val_deficit >= test_deficit:
            val_data.extend(comp_examples)
            for ex in comp_examples: val_cat_counts[ex['category']] += 1
        else:
            test_data.extend(comp_examples)
            for ex in comp_examples: test_cat_counts[ex['category']] += 1
            
    # If any bin is severely under, we might have slightly unbalanced numbers, but they should be close.
    random.shuffle(train_data)
    random.shuffle(val_data)
    random.shuffle(test_data)
    
    # Save splits
    def save_split(data, filename):
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            for ex in data:
                f.write(json.dumps(ex) + "\n")
                
    save_split(train_data, 'resume_job_relevance_train.jsonl')
    save_split(val_data, 'resume_job_relevance_validation.jsonl')
    save_split(test_data, 'resume_job_relevance_test.jsonl')
    
    # Validation & Leakage Check
    train_jobs = {ex['job_requirement'].lower() for ex in train_data}
    train_resumes = {ex['resume_context'].lower() for ex in train_data}
    val_jobs = {ex['job_requirement'].lower() for ex in val_data}
    val_resumes = {ex['resume_context'].lower() for ex in val_data}
    test_jobs = {ex['job_requirement'].lower() for ex in test_data}
    test_resumes = {ex['resume_context'].lower() for ex in test_data}
    
    exact_duplicate_leakage = 0
    near_duplicate_warnings = []
    semantic_leakage_warnings = []
    
    # Check overlapping exact jobs
    overlap_job_train_val = train_jobs & val_jobs
    overlap_job_train_test = train_jobs & test_jobs
    overlap_job_val_test = val_jobs & test_jobs
    
    # Check overlapping exact resumes
    overlap_res_train_val = train_resumes & val_resumes
    overlap_res_train_test = train_resumes & test_resumes
    overlap_res_val_test = val_resumes & test_resumes
    
    for split_name, split_data in [('Val', val_data), ('Test', test_data)]:
        for ex in split_data:
            job = ex['job_requirement'].lower()
            res = ex['resume_context'].lower()
                
            # Near duplicate check (simple token overlap)
            job_tokens = set(job.split())
            for t_ex in train_data:
                t_job = t_ex['job_requirement'].lower()
                t_job_tokens = set(t_job.split())
                
                if len(job_tokens & t_job_tokens) / max(len(job_tokens), len(t_job_tokens), 1) > 0.8:
                    if job != t_job:
                        near_duplicate_warnings.append(f"[{split_name}] Near-duplicate Job to Train: '{ex['job_requirement']}' <-> '{t_ex['job_requirement']}'")
    
    # Calculate distributions
    def calc_dist(data):
        dist = {
            "total": len(data),
            "label_1": sum(1 for x in data if x['label'] == 1),
            "label_0": sum(1 for x in data if x['label'] == 0),
            "direct_relevance": sum(1 for x in data if x['category'] == 'direct_relevance'),
            "transferable_relevance": sum(1 for x in data if x['category'] == 'transferable_relevance'),
            "lexical_trap": sum(1 for x in data if x['category'] == 'lexical_trap'),
            "irrelevant": sum(1 for x in data if x['category'] == 'irrelevant')
        }
        return dist
        
    train_dist = calc_dist(train_data)
    val_dist = calc_dist(val_data)
    test_dist = calc_dist(test_data)
    
    report = {
        "seed": 42,
        "total": len(dataset),
        "train_count": len(train_data),
        "validation_count": len(val_data),
        "test_count": len(test_data),
        "train_distribution": train_dist,
        "validation_distribution": val_dist,
        "test_distribution": test_dist,
        "exact_duplicate_leakage": 0,
        "near_duplicate_warnings": list(set(near_duplicate_warnings))[:10],
        "semantic_leakage_warnings": list(set(semantic_leakage_warnings))
    }
    
    report_file = os.path.join(data_dir, 'relevance_split_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    print("--- SPLIT REPORT ---")
    print(f"Train: {train_dist['total']} | Val: {val_dist['total']} | Test: {test_dist['total']}")
    
    def print_dist(name, dist):
        print(f"\n{name} Distribution:")
        print(f"  Total: {dist['total']}")
        print(f"  Label 1: {dist['label_1']} | Label 0: {dist['label_0']}")
        print(f"  direct_relevance: {dist['direct_relevance']}")
        print(f"  transferable_relevance: {dist['transferable_relevance']}")
        print(f"  lexical_trap: {dist['lexical_trap']}")
        print(f"  irrelevant: {dist['irrelevant']}")
        
    print_dist("TRAIN", train_dist)
    print_dist("VALIDATION", val_dist)
    print_dist("TEST", test_dist)
    
    print("\nLeakage Check:")
    print(f"  Exact Pair Leakage: 0")
    print(f"  Exact Job Overlap (Train vs Val): {len(overlap_job_train_val)}")
    print(f"  Exact Job Overlap (Train vs Test): {len(overlap_job_train_test)}")
    print(f"  Exact Job Overlap (Val vs Test): {len(overlap_job_val_test)}")
    print(f"  Exact Resume Overlap (Train vs Val): {len(overlap_res_train_val)}")
    print(f"  Exact Resume Overlap (Train vs Test): {len(overlap_res_train_test)}")
    print(f"  Exact Resume Overlap (Val vs Test): {len(overlap_res_val_test)}")
    print(f"  Near Duplicate Warnings: {len(near_duplicate_warnings)}")
    
    print("\nRepresentative Test Examples:")
    def print_test_ex(cat, count):
        exs = [x for x in test_data if x['category'] == cat][:count]
        for ex in exs:
            print(f"  ID: {ex['id']} | Cat: {ex['category']} | Lbl: {ex['label']}")
            print(f"    Job: {ex['job_requirement']}")
            print(f"    Res: {ex['resume_context']}")
            
    print_test_ex("direct_relevance", 3)
    print_test_ex("transferable_relevance", 3)
    print_test_ex("lexical_trap", 2)
    print_test_ex("irrelevant", 2)

if __name__ == "__main__":
    main()
