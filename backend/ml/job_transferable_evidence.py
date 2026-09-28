from typing import Dict, Any, List
from .transferable_evidence import find_transferable_evidence
import traceback

def analyze_job_transferable_evidence(missing_skills: List[str], resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Adapter that receives the authoritative missing_skills list from the rule-based Job Matcher,
    and returns a list of transferable evidence from the resume.
    
    ML must ONLY analyze skills already present in missing_skills.
    """
    all_evidence = []
    
    if not missing_skills:
        return all_evidence
        
    try:
        # To avoid running ML unnecessarily, we only iterate over the missing skills
        for missing_skill in missing_skills:
            # find_transferable_evidence returns a list of evidences for a given skill
            evidences = find_transferable_evidence(missing_skill, resume_data)
            
            # Filter out "not_relevant" entirely to keep payload small
            valid_evidences = [e for e in evidences if e["classification"] in ["transferable", "related_but_not_equivalent"]]
            
            # Add to the global list
            all_evidence.extend(valid_evidences)
            
    except Exception as e:
        print(f"ML Transferable Evidence failed: {e}")
        traceback.print_exc()
        # Fail gracefully
        return []
        
    return all_evidence
