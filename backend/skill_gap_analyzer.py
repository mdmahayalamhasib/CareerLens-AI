from job_analyzer import _normalize_skill

def analyze_skill_gaps(resume_data: dict, job_data: dict) -> dict:
    """
    Analyze the gap between a candidate's resume skills and the skills required
    or preferred by a job.
    """
    if not isinstance(resume_data, dict):
        resume_data = {}
    if not isinstance(job_data, dict):
        job_data = {}

    resume_skills_raw = resume_data.get("skills", [])
    if not isinstance(resume_skills_raw, list):
        resume_skills_raw = []

    normalized_resume_skills = {
        _normalize_skill(str(s)) for s in resume_skills_raw if s
    }

    required_skills = job_data.get("required_skills", [])
    if not isinstance(required_skills, list):
        required_skills = []

    preferred_skills = job_data.get("preferred_skills", [])
    if not isinstance(preferred_skills, list):
        preferred_skills = []

    skill_gaps = []
    matched_required_skills = []
    matched_preferred_skills = []

    # 1. Required skills check
    for skill in required_skills:
        if not skill:
            continue
        skill_str = str(skill)
        if _normalize_skill(skill_str) in normalized_resume_skills:
            matched_required_skills.append(skill_str)
        else:
            skill_gaps.append({
                "skill": skill_str,
                "importance": "required",
                "reason": "This skill is required for the job but was not found in the resume."
            })

    # 2. Preferred skills check
    for skill in preferred_skills:
        if not skill:
            continue
        skill_str = str(skill)
        if _normalize_skill(skill_str) in normalized_resume_skills:
            matched_preferred_skills.append(skill_str)
        else:
            skill_gaps.append({
                "skill": skill_str,
                "importance": "preferred",
                "reason": "This skill is listed as a preferred skill for the job but was not found in the resume."
            })

    # 3. Coverage Calculation
    total_required = len([s for s in required_skills if s])
    total_preferred = len([s for s in preferred_skills if s])

    required_skill_coverage = None
    if total_required > 0:
        required_skill_coverage = round((len(matched_required_skills) / total_required) * 100)

    preferred_skill_coverage = None
    if total_preferred > 0:
        preferred_skill_coverage = round((len(matched_preferred_skills) / total_preferred) * 100)

    # 4. Summary Generation
    if total_required == 0:
        summary = "No required skills were detected in the job description."
    elif len(matched_required_skills) == total_required:
        summary = "All required skills were found in the resume."
    else:
        summary = f"The resume matches {len(matched_required_skills)} of {total_required} required skills and {len(matched_preferred_skills)} of {total_preferred} preferred skills."

    return {
        "skill_gaps": skill_gaps,
        "matched_required_skills": matched_required_skills,
        "matched_preferred_skills": matched_preferred_skills,
        "required_skill_coverage": required_skill_coverage,
        "preferred_skill_coverage": preferred_skill_coverage,
        "summary": summary
    }
