import json
import os
import sys

def validate():
    filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'resume_job_relevance_golden.jsonl')
    
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        sys.exit(1)

    data = []
    ids = set()
    errors = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                data.append(obj)
                
                # Check required fields
                required_fields = ["id", "job_requirement", "resume_context", "label", "category", "reason"]
                for field in required_fields:
                    if field not in obj:
                        errors.append(f"Line {i+1}: Missing field '{field}'")
                    elif obj[field] == "":
                        errors.append(f"Line {i+1}: Empty field '{field}'")
                        
                # Check IDs
                if "id" in obj:
                    if obj["id"] in ids:
                        errors.append(f"Line {i+1}: Duplicate ID '{obj['id']}'")
                    ids.add(obj["id"])
                    
                # Check label
                if "label" in obj and obj["label"] not in [0, 1]:
                    errors.append(f"Line {i+1}: Invalid label '{obj['label']}'")
                    
                # Check categories
                valid_categories = ["direct_relevance", "transferable_relevance", "lexical_trap", "irrelevant"]
                if "category" in obj and obj["category"] not in valid_categories:
                    errors.append(f"Line {i+1}: Invalid category '{obj['category']}'")
                    
            except json.JSONDecodeError:
                errors.append(f"Line {i+1}: Invalid JSON")

    # Check totals
    if len(data) != 100:
        errors.append(f"Expected 100 examples, found {len(data)}")

    categories = {}
    labels = {0: 0, 1: 0}
    
    for obj in data:
        cat = obj.get("category")
        categories[cat] = categories.get(cat, 0) + 1
        
        lbl = obj.get("label")
        if lbl in labels:
            labels[lbl] += 1

    print("--- VALIDATION REPORT ---")
    print(f"Total Examples: {len(data)}")
    print(f"Label 1 Count: {labels[1]}")
    print(f"Label 0 Count: {labels[0]}")
    print("\nCategory Distribution:")
    for k, v in categories.items():
        print(f"  {k}: {v}")
        
    print("\nRepresentative Examples:")
    
    def print_examples(cat, count):
        print(f"\n[{cat}]")
        exs = [x for x in data if x.get("category") == cat][:count]
        for ex in exs:
            print(f"  Job: {ex['job_requirement']}")
            print(f"  Resume: {ex['resume_context']}")
            print(f"  Label: {ex['label']} | Reason: {ex['reason']}\n")

    print_examples("direct_relevance", 3)
    print_examples("transferable_relevance", 2)
    print_examples("lexical_trap", 3)
    print_examples("irrelevant", 2)

    if errors:
        print("\n--- VALIDATION ERRORS ---")
        for err in errors:
            print(err)
        sys.exit(1)
    else:
        print("\nValidation passed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    validate()
