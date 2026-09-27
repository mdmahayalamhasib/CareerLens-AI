from typing import Dict, List, Any
from .relevance_api import analyze_relevance

def apply_business_rules(missing_skill: str, evidence_text: str, ml_score: float, ml_relevant: bool) -> str:
    """
    Applies conservative business rules to the ML output to prevent 
    lexical traps from falsely classifying as transferable.
    
    Returns one of: "transferable", "related_but_not_equivalent", "not_relevant"
    """
    if not ml_relevant or ml_score < 0.50:
        return "not_relevant"
        
    ms_lower = missing_skill.lower()
    ev_lower = evidence_text.lower()
    
    # TRAP 1: Kubernetes vs Docker
    if "kubernetes" in ms_lower and "docker" in ev_lower and "kubernetes" not in ev_lower:
        return "related_but_not_equivalent"
        
    # TRAP 2: React vs Angular / Vue
    if "react" in ms_lower and ("angular" in ev_lower or "vue" in ev_lower) and "react" not in ev_lower:
        return "related_but_not_equivalent"
        
    # TRAP 3: Java vs JavaScript
    # Often models see Java and JavaScript as highly related programming contexts
    if "java" in ms_lower and "javascript" not in ms_lower:
        # If evidence mentions javascript but not java
        # Make sure 'java' standalone isn't in evidence
        # regex boundary check is safer but simple string manipulation works for this demo
        import re
        has_java = bool(re.search(r'\bjava\b', ev_lower))
        has_js = bool(re.search(r'\bjavascript\b', ev_lower))
        if has_js and not has_java:
            # ML might have scored it high due to "programming/web"
            return "not_relevant" 

    # If it passed the strict traps and ML says it's relevant, it is potentially transferable
    return "transferable"

def find_transferable_evidence(missing_skill: str, resume_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Scans a resume for potential transferable evidence of a missing skill.
    ML relevance does NOT change exact skill matching.
    """
    evidences = []
    
    # 1. Scan Projects
    projects = resume_data.get("projects", [])
    for proj in projects:
        title = proj.get("name", "Unknown Project")
        desc = proj.get("description", "")
        tech = ", ".join(proj.get("technologies", []))
        
        context = f"Project {title}: {desc} Technologies used: {tech}"
        
        ml_res = analyze_relevance(f"Experience with {missing_skill}", context)
        classification = apply_business_rules(
            missing_skill, 
            context, 
            ml_res["relevance_score"], 
            ml_res["is_relevant"]
        )
        
        if classification != "not_relevant":
            evidences.append({
                "skill": missing_skill,
                "source_type": "project",
                "source_title": title,
                "evidence_text": desc if desc else tech,
                "relevance_score": ml_res["relevance_score"],
                "classification": classification
            })
            
    # 2. Scan Experience
    experiences = resume_data.get("experience", [])
    for exp in experiences:
        title = exp.get("role", "Unknown Role")
        company = exp.get("company", "Unknown Company")
        desc = exp.get("description", "")
        
        context = f"Role {title} at {company}: {desc}"
        
        ml_res = analyze_relevance(f"Experience with {missing_skill}", context)
        classification = apply_business_rules(
            missing_skill, 
            context, 
            ml_res["relevance_score"], 
            ml_res["is_relevant"]
        )
        
        if classification != "not_relevant":
            evidences.append({
                "skill": missing_skill,
                "source_type": "experience",
                "source_title": f"{title} at {company}",
                "evidence_text": desc,
                "relevance_score": ml_res["relevance_score"],
                "classification": classification
            })
            
    # Sort evidences by score descending
    evidences.sort(key=lambda x: x["relevance_score"], reverse=True)
    return evidences
