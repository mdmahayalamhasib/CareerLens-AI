import json
import os
import time
import sys

def get_data_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def get_dir_size(path):
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def main():
    data_dir = get_data_dir()
    test_file = os.path.join(data_dir, 'resume_job_relevance_test.jsonl')
    model_dir = os.path.join(os.path.dirname(__file__), 'models', 'mpnet_relevance_finetuned')
    
    # 1. Model size
    if not os.path.exists(model_dir):
        print("Error: Model dir not found")
        sys.exit(1)
        
    model_size_mb = get_dir_size(model_dir) / (1024 * 1024)
    
    # Load test examples
    examples = []
    with open(test_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                examples.append(json.loads(line))
                
    # We want at least 20 pairs. Test set has 30.
    test_pairs = examples[:20]
    
    # 2. Measure load time
    start_load = time.time()
    from relevance_api import analyze_relevance
    from relevance_model import load_relevance_model, RELEVANCE_THRESHOLD
    
    # Force initialization
    load_relevance_model()
    load_time = time.time() - start_load
    
    # 3. Single inference time (coldish)
    ex = test_pairs[0]
    start_single = time.time()
    analyze_relevance(ex['job_requirement'], ex['resume_context'])
    single_inf_time = time.time() - start_single
    
    # 4. Average / min / max inference
    times = []
    for ex in test_pairs:
        t0 = time.time()
        analyze_relevance(ex['job_requirement'], ex['resume_context'])
        t1 = time.time()
        times.append(t1 - t0)
        
    avg_inf_time = sum(times) / len(times)
    min_inf_time = min(times)
    max_inf_time = max(times)
    
    benchmark = {
        "model": "fine-tuned all-mpnet-base-v2",
        "threshold": RELEVANCE_THRESHOLD,
        "model_size_mb": round(model_size_mb, 2),
        "load_time_seconds": round(load_time, 4),
        "single_inference_seconds": round(single_inf_time, 4),
        "average_inference_seconds": round(avg_inf_time, 4),
        "min_inference_seconds": round(min_inf_time, 4),
        "max_inference_seconds": round(max_inf_time, 4),
        "test_examples_used_for_benchmark": len(test_pairs)
    }
    
    out_path = os.path.join(data_dir, 'relevance_model_benchmark.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(benchmark, f, indent=2)
        
    print("\n=== BENCHMARK REPORT ===")
    print(f"Model Size: {benchmark['model_size_mb']} MB")
    print(f"Load Time:  {benchmark['load_time_seconds']} sec")
    print(f"Single Inference:  {benchmark['single_inference_seconds']} sec")
    print(f"Average Inference: {benchmark['average_inference_seconds']} sec")
    print(f"Min Inference:     {benchmark['min_inference_seconds']} sec")
    print(f"Max Inference:     {benchmark['max_inference_seconds']} sec")
    
if __name__ == "__main__":
    main()
