from collections import Counter

def generate_interview_summary(evaluations: list[dict]) -> dict:
    """
    Generate an overall summary from multiple interview answer evaluations.
    """
    if not isinstance(evaluations, list) or not evaluations:
        return {
            "overall_score": 0.0,
            "total_questions": 0,
            "answered_questions": 0,
            "average_score": 0.0,
            "strengths": [],
            "areas_to_improve": [],
            "recommendation": "No interview answers were provided."
        }
    
    total_questions = len(evaluations)
    answered_questions = 0
    total_score = 0
    
    all_strengths = []
    all_improvements = []
    
    for eval_item in evaluations:
        # Handle malformed items safely
        if not isinstance(eval_item, dict):
            continue
            
        score = eval_item.get("score", 0)
        
        if isinstance(score, (int, float)):
            total_score += score
            if score > 0:
                answered_questions += 1
                
        strengths = eval_item.get("strengths", [])
        if isinstance(strengths, list):
            all_strengths.extend([s for s in strengths if isinstance(s, str)])
            
        improvements = eval_item.get("improvements", [])
        if isinstance(improvements, list):
            all_improvements.extend([i for i in improvements if isinstance(i, str)])

    average_score = 0.0
    if total_questions > 0:
        average_score = round(total_score / total_questions, 1)

    # Count frequencies to sort by most repeated items first
    strength_counts = Counter(all_strengths)
    improvement_counts = Counter(all_improvements)
    
    # Sort by frequency and limit to max 5 items
    sorted_strengths = [item for item, _ in strength_counts.most_common(5)]
    sorted_improvements = [item for item, _ in improvement_counts.most_common(5)]
    
    # Recommendation logic based on average score
    if average_score < 4:
        recommendation = "Focus on providing longer, more detailed answers and explaining your reasoning."
    elif 4 <= average_score < 7:
        recommendation = "Improve technical depth and support your answers with concrete examples."
    elif 7 <= average_score < 9:
        recommendation = "Good overall performance. Focus on adding more precise technical details and examples."
    else:
        recommendation = "Excellent overall performance. Continue practicing concise and technically detailed answers."
        
    return {
        "overall_score": average_score,
        "total_questions": total_questions,
        "answered_questions": answered_questions,
        "average_score": average_score,
        "strengths": sorted_strengths,
        "areas_to_improve": sorted_improvements,
        "recommendation": recommendation
    }
