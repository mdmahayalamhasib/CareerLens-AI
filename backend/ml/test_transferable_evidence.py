import json
import os
import sys

def get_data_dir():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def build_mock_resume(project_desc, project_tech):
    return {
        "projects": [
            {
                "name": "Test Project",
                "description": project_desc,
                "technologies": project_tech
            }
        ],
        "experience": []
    }

def main():
    print("Loading dependencies...")
    from .transferable_evidence import find_transferable_evidence
    
    test_cases = [
        {
            "id": "CASE_1",
            "missing_skill": "PostgreSQL",
            "resume_desc": "Built applications using MySQL and complex SQL queries.",
            "resume_tech": ["MySQL", "SQL"],
            "expected_classification": "transferable"
        },
        {
            "id": "CASE_2",
            "missing_skill": "Machine Learning",
            "resume_desc": "Trained classification models using Python and scikit-learn.",
            "resume_tech": ["Python", "scikit-learn"],
            "expected_classification": "transferable"
        },
        {
            "id": "CASE_3",
            "missing_skill": "REST API",
            "resume_desc": "Built a FastAPI backend with HTTP endpoints.",
            "resume_tech": ["FastAPI", "Python"],
            "expected_classification": "transferable"
        },
        {
            "id": "CASE_4",
            "missing_skill": "Kubernetes",
            "resume_desc": "Containerized applications using Docker.",
            "resume_tech": ["Docker"],
            "expected_classification": "related_but_not_equivalent"
        },
        {
            "id": "CASE_5",
            "missing_skill": "React",
            "resume_desc": "Built an Angular web application.",
            "resume_tech": ["Angular", "TypeScript"],
            "expected_classification": "related_but_not_equivalent"
        },
        {
            "id": "CASE_6",
            "missing_skill": "Java",
            "resume_desc": "Built a JavaScript web application.",
            "resume_tech": ["JavaScript", "Node.js"],
            "expected_classification": "not_relevant"
        },
        {
            "id": "CASE_7",
            "missing_skill": "PostgreSQL",
            "resume_desc": "Designed logos and branding materials.",
            "resume_tech": ["Adobe Illustrator", "Photoshop"],
            "expected_classification": "not_relevant"
        }
    ]
    
    results = []
    
    for tc in test_cases:
        print(f"\nEvaluating {tc['id']}...")
        resume_data = build_mock_resume(tc["resume_desc"], tc["resume_tech"])
        
        evidences = find_transferable_evidence(tc["missing_skill"], resume_data)
        
        # If no evidence returned, classification is inherently "not_relevant"
        actual_class = evidences[0]["classification"] if evidences else "not_relevant"
        score = evidences[0]["relevance_score"] if evidences else 0.0
        
        passed = actual_class == tc["expected_classification"]
        
        print(f"Missing Skill: {tc['missing_skill']}")
        print(f"Resume: {tc['resume_desc']}")
        print(f"Expected: {tc['expected_classification']} | Actual: {actual_class}")
        print(f"Score: {score:.3f} | PASS: {passed}")
        
        results.append({
            "test_case_id": tc["id"],
            "missing_skill": tc["missing_skill"],
            "resume_evidence_tested": tc["resume_desc"],
            "expected_classification": tc["expected_classification"],
            "actual_classification": actual_class,
            "relevance_score": score,
            "pass": passed,
            "explanation": "Passed" if passed else "Classification mismatch"
        })
        
    output = {
        "safety_rule_enforcement": "ML relevance does not change exact skill matching.",
        "test_cases_evaluated": len(test_cases),
        "results": results
    }
    
    data_dir = get_data_dir()
    out_file = os.path.join(data_dir, 'transferable_evidence_evaluation.json')
    
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
        
    print("\nEvaluation saved to:", out_file)
    print("Remember: ML relevance does not change exact skill matching.")

if __name__ == "__main__":
    main()
