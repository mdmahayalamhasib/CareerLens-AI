def generate_interview_questions(job_data: dict, resume_data: dict) -> list[dict]:
    """
    Generate a deterministic list of interview questions based on job requirements
    and resume details.
    """
    questions = []
    seen_questions = set()

    def add_question(q_text: str, q_type: str, skill: str = None) -> None:
        if q_text not in seen_questions and len(questions) < 10:
            q = {
                "question": q_text,
                "type": q_type,
            }
            if skill:
                q["skill"] = skill
            
            questions.append(q)
            seen_questions.add(q_text)

    # Handle missing or None fields gracefully
    if not job_data:
        job_data = {}
    if not resume_data:
        resume_data = {}

    req_skills = job_data.get("required_skills", []) or []
    pref_skills = job_data.get("preferred_skills", []) or []
    projects = resume_data.get("projects", []) or []

    # 1. Generate technical questions for required skills
    for skill in req_skills:
        skill_lower = skill.lower()
        if skill_lower == "python":
            q_text = "How would you use Python to build a backend application?"
        elif skill_lower == "fastapi":
            q_text = "How would you design a REST API using FastAPI?"
        elif skill_lower == "postgresql":
            q_text = "How would you design and optimize a PostgreSQL database?"
        elif skill_lower == "git":
            q_text = "Describe how you use Git in a software development workflow?"
        else:
            q_text = f"Can you explain your experience with {skill} and how you have applied it in previous work?"
            
        add_question(q_text, "technical", skill)

    # 2. Generate technical questions for preferred skills (lower priority)
    for skill in pref_skills:
        q_text = f"What is your proficiency level with {skill}, and can you provide an example of when you used it?"
        add_question(q_text, "technical", skill)

    # 3. Generate project questions
    for proj in projects:
        if isinstance(proj, dict):
            proj_name = proj.get("name", "recent")
            techs = proj.get("technologies", [])
        else:
            proj_name = str(proj)
            techs = []

        if techs:
            tech_str = f" and the role {', '.join(techs)} played in it"
        else:
            tech_str = ""

        q_text = f"Explain your {proj_name} project{tech_str}."
        add_question(q_text, "project")

    # 4. Generate behavioral questions
    add_question(
        "Describe a technical challenge you faced in one of your projects and how you solved it.",
        "behavioral"
    )

    # Pad to at least 5 questions if we don't have enough
    fallback_behavioral = [
        "Tell me about a time you had to learn a new technology quickly.",
        "How do you prioritize tasks when you have multiple deadlines?",
        "Describe a situation where you had to debug a complex issue. What was your approach?",
        "What do you consider your greatest technical achievement so far?"
    ]
    
    for fallback in fallback_behavioral:
        if len(questions) >= 5:
            break
        add_question(fallback, "behavioral")

    return questions
