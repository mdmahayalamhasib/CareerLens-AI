import re

TECHNICAL_KEYWORDS = {
    "python": {"python", "function", "class", "module", "exception", "list", "dictionary", "api"},
    "fastapi": {"fastapi", "endpoint", "route", "request", "response", "validation", "http", "api", "pydantic", "status"},
    "postgresql": {"postgresql", "database", "table", "query", "index", "join", "transaction", "normalization"},
    "git": {"git", "commit", "branch", "merge", "pull", "push", "repository"},
    "rest api": {"rest", "api", "endpoint", "http", "get", "post", "put", "delete", "request", "response", "status code", "status"},
    "docker": {"docker", "container", "image", "dockerfile", "deployment"}
}

DEFAULT_TECHNICAL_KEYWORDS = {
    "api", "endpoint", "http", "get", "post", "database", "query", 
    "code", "function", "class", "design", "architecture", 
    "validation", "error", "test", "deployment"
}

PROJECT_KEYWORDS = {
    "project", "technology", "feature", "implementation", "contribution", 
    "challenge", "solution", "database", "api", "deployment", "built", "designed"
}

BEHAVIORAL_KEYWORDS = {
    "situation", "context", "problem", "challenge", "action", 
    "solution", "result", "outcome", "team", "conflict", "learned"
}


def evaluate_interview_answer(question: dict, answer: str) -> dict:
    if not isinstance(answer, str) or not answer.strip():
        return {
            "score": 0,
            "strengths": [],
            "improvements": ["No answer was provided."],
            "feedback": "Please provide an answer to the interview question."
        }
        
    answer_clean = answer.strip().lower()
    words = re.findall(r'\b\w+\b', answer_clean)
    word_count = len(words)
    
    score = 0
    strengths = []
    improvements = []
    
    if not isinstance(question, dict):
        question = {}
        
    q_type = question.get("type", "technical")
    if not q_type or not isinstance(q_type, str):
        q_type = "technical"
    else:
        q_type = q_type.lower()
        
    skill = question.get("skill", "")
    if not skill or not isinstance(skill, str):
        skill = ""
    skill_lower = skill.lower()

    # 1. Base Score based on length
    if word_count < 10:
        score += 1
        improvements.append("Add more technical details.")
    elif word_count < 30:
        score += 3
        improvements.append("Include a practical example.")
    else:
        score += 5
        strengths.append("Provided a detailed explanation.")

    # 2. Extract keywords based on question type
    if q_type == "technical":
        # Check skill-specific keywords
        keywords_to_check = TECHNICAL_KEYWORDS.get(skill_lower, DEFAULT_TECHNICAL_KEYWORDS)
        
        found = [kw for kw in keywords_to_check if kw in answer_clean]
        
        if len(found) >= 3:
            score += 4
            strengths.append(f"Used relevant {skill if skill else 'technical'} concepts.")
        elif len(found) > 0:
            score += 2
            strengths.append("Mentioned some relevant technical terms.")
            improvements.append("Explain the implementation more clearly.")
        else:
            improvements.append("Mention relevant technical concepts and implementation details.")

        # Special check for REST API / HTTP details
        if "fastapi" in skill_lower or "rest" in skill_lower:
            if "get" in answer_clean or "post" in answer_clean or "status" in answer_clean:
                score += 1
                strengths.append("Mentioned HTTP methods and status codes.")
            else:
                improvements.append("Mention relevant HTTP methods and status codes.")
                
    elif q_type == "project":
        found = [kw for kw in PROJECT_KEYWORDS if kw in answer_clean]
        
        if len(found) >= 4:
            score += 4
            strengths.append("Explained the project details clearly.")
        elif len(found) > 0:
            score += 2
            improvements.append("Add more details about your specific contribution and the technologies used.")
        else:
            improvements.append("Explain what the project does and the technical challenges you faced.")
            
    elif q_type == "behavioral":
        found = [kw for kw in BEHAVIORAL_KEYWORDS if kw in answer_clean]
        
        if len(found) >= 3:
            score += 4
            strengths.append("Explained the situation, action, and outcome clearly.")
        elif len(found) > 0:
            score += 2
            improvements.append("Describe the result or outcome.")
        else:
            improvements.append("Explain the situation, the action you took, and the final result.")
            
    else:
        # Unknown question type fallback
        if word_count >= 20:
            score += 3
            
    # Cap score
    score = min(10, score)
    
    # Generate concise feedback
    if score >= 8:
        feedback = f"Good {q_type} answer with relevant concepts, but a concrete example could make it even stronger."
        if "practical example" in str(strengths).lower() or word_count > 40:
            feedback = f"Excellent {q_type} answer with strong relevant concepts and good detail."
    elif score >= 4:
        feedback = f"Acceptable answer, but you should include more specific details and relevant terminology."
    else:
        feedback = "The answer is too brief and lacks necessary explanation and context."

    # Deduplicate strengths and improvements
    strengths = list(dict.fromkeys(strengths))[:3]
    improvements = list(dict.fromkeys(improvements))[:3]

    return {
        "score": score,
        "strengths": strengths,
        "improvements": improvements,
        "feedback": feedback
    }
