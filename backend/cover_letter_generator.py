from job_analyzer import _normalize_skill

def create_cover_letter(resume_data: dict, job_data: dict) -> dict:
    """
    Generate a deterministic cover letter based on resume and job data.
    """
    if not isinstance(resume_data, dict):
        resume_data = {}
    if not isinstance(job_data, dict):
        job_data = {}

    candidate_name = resume_data.get("name", "").strip()
    if not candidate_name:
        candidate_name = "[Your Name]"

    job_title = job_data.get("job_title", "").strip()
    if not job_title:
        job_title = "open"

    # Match skills
    resume_skills_raw = resume_data.get("skills", [])
    if not isinstance(resume_skills_raw, list):
        resume_skills_raw = []
    
    normalized_resume_skills = {
        _normalize_skill(str(s)) for s in resume_skills_raw if isinstance(s, str)
    }

    required_skills = job_data.get("required_skills", [])
    if not isinstance(required_skills, list):
        required_skills = []

    matched_skills = []
    for skill in required_skills:
        if isinstance(skill, str) and skill.strip():
            if _normalize_skill(skill) in normalized_resume_skills:
                matched_skills.append(skill.strip())
                
    # Keep up to 3 matched skills
    matched_skills_highlighted = matched_skills[:3]

    # Process projects
    projects_raw = resume_data.get("projects", [])
    if not isinstance(projects_raw, list):
        projects_raw = []
        
    valid_projects = []
    for p in projects_raw:
        if isinstance(p, dict):
            name = p.get("name")
            if name and isinstance(name, str) and name.strip():
                valid_projects.append(name.strip())
        elif isinstance(p, str) and p.strip():
            valid_projects.append(p.strip())
            
    # Keep up to 2 projects
    projects_highlighted = valid_projects[:2]

    # Determine template
    if matched_skills_highlighted and projects_highlighted:
        template_used = "technical_project_focused"
    elif matched_skills_highlighted:
        template_used = "skills_focused"
    else:
        template_used = "generic"

    # Formatting skills string
    if len(matched_skills_highlighted) == 1:
        skills_str = matched_skills_highlighted[0]
    elif len(matched_skills_highlighted) == 2:
        skills_str = f"{matched_skills_highlighted[0]} and {matched_skills_highlighted[1]}"
    elif len(matched_skills_highlighted) == 3:
        skills_str = f"{matched_skills_highlighted[0]}, {matched_skills_highlighted[1]}, and {matched_skills_highlighted[2]}"
    else:
        skills_str = ""

    # Formatting projects string
    if len(projects_highlighted) == 1:
        projects_str = projects_highlighted[0]
        project_word = "project demonstrates"
    elif len(projects_highlighted) == 2:
        projects_str = f"{projects_highlighted[0]} and {projects_highlighted[1]}"
        project_word = "projects demonstrate"
    else:
        projects_str = ""
        project_word = "projects demonstrate"

    # Generate content based on template
    body = ""
    if template_used == "technical_project_focused":
        body = (
            f"Dear Hiring Manager,\n\n"
            f"I am writing to express my strong interest in the {job_title} position. "
            f"Based on the job requirements, my technical background strongly aligns with your needs.\n\n"
            f"Specifically, my proficiency in {skills_str} has allowed me to build impactful solutions. "
            f"For example, my work on the {projects_str} {project_word} my ability to apply these technologies effectively to solve real-world problems.\n\n"
            f"I would welcome the opportunity to discuss how my skills and experience can contribute to your team's success. "
            f"Thank you for considering my application.\n\n"
            f"Sincerely,\n{candidate_name}"
        )
        summary = f"Cover letter generated successfully using the technical/project-focused template with {len(matched_skills_highlighted)} matched skill(s) and {len(projects_highlighted)} project(s)."
        
    elif template_used == "skills_focused":
        body = (
            f"Dear Hiring Manager,\n\n"
            f"I am writing to express my strong interest in the {job_title} position. "
            f"My technical background and enthusiasm for software development make me a strong candidate for this role.\n\n"
            f"Through my experience, I have developed a solid foundation in key technologies required for this position, including {skills_str}. "
            f"I am confident in my ability to quickly adapt and contribute effectively to your team's ongoing projects.\n\n"
            f"I would appreciate the opportunity to discuss my qualifications further. "
            f"Thank you for your time and consideration.\n\n"
            f"Sincerely,\n{candidate_name}"
        )
        summary = f"Cover letter generated successfully using the skills-focused template highlighting {len(matched_skills_highlighted)} skill(s)."

    else:
        body = (
            f"Dear Hiring Manager,\n\n"
            f"I am writing to express my strong interest in the {job_title} position. "
            f"I am passionate about building high-quality solutions and am eager to bring my dedication to your team.\n\n"
            f"My background has equipped me with a strong foundation in problem-solving and collaboration. "
            f"I am highly motivated to leverage my skills and continue growing as a professional within your organization.\n\n"
            f"I would welcome the opportunity to discuss how my background aligns with your needs. "
            f"Thank you for considering my application.\n\n"
            f"Sincerely,\n{candidate_name}"
        )
        summary = "Cover letter generated successfully using the generic template."

    return {
        "cover_letter": body,
        "matched_skills_highlighted": matched_skills_highlighted,
        "template_used": template_used,
        "summary": summary
    }
