from typing import Dict, Any
from .relevance_model import calculate_relevance

def analyze_relevance(job_requirement: str, resume_context: str) -> Dict[str, Any]:
    """
    Isolated API endpoint function for contextual semantic relevance.
    Evaluates whether the resume_context provides meaningful evidence 
    for the job_requirement.
    """
    # Simply wrap the model layer to act as the clean service boundary.
    # We explicitly do NOT return any "has_skill" fields here, as
    # semantic relevance is conceptually distinct from exact skill ownership.
    return calculate_relevance(job_requirement, resume_context)
