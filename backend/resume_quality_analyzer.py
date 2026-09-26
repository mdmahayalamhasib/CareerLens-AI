import re

ACTION_VERBS = {
    "developed", "built", "created", "designed", "implemented", "led", "managed",
    "improved", "optimized", "analyzed", "deployed", "automated", "integrated",
    "tested", "maintained", "configured"
}
METRICS_PATTERN = re.compile(r"\d+")

def analyze_resume_quality(resume_data: dict) -> dict:
    """
    Deterministically evaluates the quality/completeness of structured resume_data.
    """
    if not isinstance(resume_data, dict):
        resume_data = {}
        
    score = 0
    strengths = []
    improvements = []
    
    # 1. Contact Info
    has_email = bool(resume_data.get("email"))
    has_phone = bool(resume_data.get("phone"))
    has_location = bool(resume_data.get("location"))
    
    if has_email: score += 5
    if has_phone: score += 5
    if has_location: score += 5
    
    # 2. Core Sections
    skills = resume_data.get("skills", [])
    has_skills = isinstance(skills, list) and len(skills) > 0
    if has_skills: score += 10
    
    experience = resume_data.get("experience", [])
    has_experience = isinstance(experience, list) and len(experience) > 0
    if has_experience: score += 10
    
    education = resume_data.get("education", [])
    has_education = isinstance(education, list) and len(education) > 0
    if has_education: score += 10
    
    # 3. Professional Links
    has_linkedin = bool(resume_data.get("linkedin"))
    if has_linkedin: score += 5
    
    has_github = bool(resume_data.get("github"))
    if has_github: score += 5
    
    # 4. Supplemental Sections
    projects = resume_data.get("projects", [])
    has_projects = isinstance(projects, list) and len(projects) > 0
    if has_projects: score += 10
    
    certifications = resume_data.get("certifications", [])
    has_certifications = isinstance(certifications, list) and len(certifications) > 0
    
    leadership = resume_data.get("leadership", [])
    has_leadership = isinstance(leadership, list) and len(leadership) > 0
    
    if has_certifications or has_leadership:
        score += 5
        
    # 5. Content Quality
    all_descriptions = []
    if isinstance(experience, list):
        for exp in experience:
            if isinstance(exp, str):
                all_descriptions.append(exp.lower())
    if isinstance(projects, list):
        for proj in projects:
            if isinstance(proj, dict):
                desc = proj.get("description", "")
                if isinstance(desc, str):
                    all_descriptions.append(desc.lower())
            elif isinstance(proj, str):
                all_descriptions.append(proj.lower())
                
    combined_text = " ".join(all_descriptions)
    
    # Note: Regex word boundary ensures we don't match substrings incorrectly
    # However, simple "in" check is robust enough for this deterministic heuristic list
    has_action_verbs = any(verb in combined_text for verb in ACTION_VERBS)
    if has_action_verbs:
        score += 15
        
    has_metrics = bool(METRICS_PATTERN.search(combined_text))
    if has_metrics:
        score += 15
        
    # Build Section Status
    section_status = {
        "required": {
            "contact_info": has_email and has_phone and has_location,
            "skills": has_skills,
            "experience": has_experience,
            "education": has_education
        },
        "recommended": {
            "linkedin": has_linkedin,
            "github": has_github,
            "projects": has_projects
        },
        "optional": {
            "certifications": has_certifications,
            "leadership": has_leadership
        }
    }
    
    # Build Strengths & Improvements
    if has_email and has_phone and has_location:
        strengths.append("Contact information is complete.")
    else:
        missing = []
        if not has_email: missing.append("email")
        if not has_phone: missing.append("phone")
        if not has_location: missing.append("location")
        improvements.append(f"Complete your contact information (missing: {', '.join(missing)}).")
        
    if has_skills and has_experience and has_education:
        strengths.append("All core sections (skills, experience, education) are present.")
    else:
        if not has_skills: improvements.append("Add a skills section.")
        if not has_experience: improvements.append("Add a work experience section.")
        if not has_education: improvements.append("Add an educational background section.")
        
    if has_linkedin and has_github:
        strengths.append("Professional links (LinkedIn and GitHub) are included.")
    elif has_linkedin or has_github:
        strengths.append("A professional link is included.")
        improvements.append("Consider adding more professional links (e.g., GitHub or portfolio).")
    else:
        improvements.append("Include professional links such as LinkedIn or GitHub.")
        
    if has_projects:
        strengths.append("Projects section is present to showcase practical work.")
    else:
        improvements.append("Consider adding a projects section to highlight practical experience.")
        
    if has_action_verbs:
        strengths.append("Experience/project descriptions use strong action verbs.")
    else:
        improvements.append("Use strong action verbs (e.g., developed, led, built) in your descriptions.")
        
    if has_metrics:
        strengths.append("Descriptions contain measurable/quantifiable achievements.")
    else:
        improvements.append("Add quantifiable metrics (numbers, percentages) to your descriptions to show impact.")
        
    # ATS Readiness Categories
    if score < 50:
        ats_readiness = "Needs Work (ATS Readiness Heuristic)"
    elif score <= 80:
        ats_readiness = "Moderate (ATS Readiness Heuristic)"
    else:
        ats_readiness = "Strong (ATS Readiness Heuristic)"
        
    return {
        "quality_analysis": {
            "overall_score": score,
            "section_status": section_status,
            "strengths": strengths,
            "improvements": improvements,
            "ats_readiness": ats_readiness
        }
    }
