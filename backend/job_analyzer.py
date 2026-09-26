"""
Job description analysis and resume-to-job matching.
Rule-based (regex + heading detection + a small skill vocabulary) for this
first version — no LLM, embeddings, or external API calls.
Designed to be upgraded later without changing the public function
signatures: analyze_job_description(str) -> dict and
match_resume_to_job(dict, dict) -> dict.
"""

import re


# ---------------------------------------------------------------------------
# Skill vocabulary: canonical names + alias -> canonical mapping.
# This is intentionally a small, extensible list, not exhaustive.
# Add more entries here as you encounter skills it misses.
# ---------------------------------------------------------------------------

KNOWN_SKILLS = [
    "Python", "JavaScript", "TypeScript", "Java", "PHP", "SQL", "R",
    "FastAPI", "Django", "Flask", "React", "Next.js", "Vue", "Angular",
    "Node.js", "Express",
    "PostgreSQL", "MySQL", "MongoDB", "SQLite", "Redis",
    "Docker", "Kubernetes", "AWS", "Azure", "GCP",
    "Git", "GitHub", "REST API", "GraphQL", "WebSockets", "JWT",
    "Tailwind CSS", "HTML", "CSS",
    "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
]

# alias (lowercase, as it might appear in text) -> canonical name.
# Note: "C" and other single-letter/ambiguous terms are deliberately left
# out of this vocabulary to avoid unreliable partial matches.
SKILL_ALIASES = {
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "rest api": "REST API",
    "rest apis": "REST API",
    "restful api": "REST API",
    "restful apis": "REST API",
}

# Build the full lookup: canonical names map to themselves, plus aliases.
SKILL_LOOKUP: dict[str, str] = {name: name for name in KNOWN_SKILLS}
SKILL_LOOKUP.update(SKILL_ALIASES)


def _build_term_pattern(term: str) -> re.Pattern:
    """
    Build a case-insensitive pattern that matches `term` only when it isn't
    directly attached to other letters/digits. This is what stops "Java"
    from matching inside "JavaScript" without needing a manual exception.
    """
    escaped = re.escape(term)
    return re.compile(rf"(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])", re.IGNORECASE)


# Pre-compile once at import time.
_SKILL_PATTERNS: dict[str, re.Pattern] = {
    term: _build_term_pattern(term) for term in SKILL_LOOKUP
}


def _find_known_skills(text: str) -> list[str]:
    """
    Scan `text` for any known skill (or alias) and return the canonical
    names found, ordered by where they first appear in the text.
    """
    if not text:
        return []

    first_position: dict[str, int] = {}
    for term, canonical in SKILL_LOOKUP.items():
        match = _SKILL_PATTERNS[term].search(text)
        if match:
            pos = match.start()
            if canonical not in first_position or pos < first_position[canonical]:
                first_position[canonical] = pos

    return [name for name, _ in sorted(first_position.items(), key=lambda kv: kv[1])]


def _normalize_skill(raw_skill: str) -> str:
    """
    Map a raw skill string (from a resume or job description) to its
    canonical form if it's a known skill; otherwise return it stripped
    and unchanged. Used so "python" and "Python" compare as equal.
    """
    cleaned = raw_skill.strip()
    return SKILL_LOOKUP.get(cleaned.lower(), cleaned)


# ---------------------------------------------------------------------------
# Job description section detection (structured JDs with headings)
# ---------------------------------------------------------------------------

JD_SECTION_HEADINGS = {
    "required_skills": ["requirements", "required skills", "must have", "must-have"],
    "preferred_skills": [
        "preferred",
        "preferred skills",
        "nice to have",
        "nice-to-have",
    ],
    "responsibilities": ["responsibilities", "key responsibilities", "duties"],
    "qualifications": ["qualifications", "education requirements"],
}

BULLET_PREFIX_PATTERN = re.compile(r"^[•▪◦·*-]\s*")

# Matches phrases like "3+ years", "3-5 years", "5 years" — used to spot
# experience requirements anywhere in the text, not just under one heading.
EXPERIENCE_PATTERN = re.compile(
    r"\b\d+\+?\s*(?:-\s*\d+\s*)?\+?\s*years?\b", re.IGNORECASE
)


def _matches_jd_heading(lower_line: str) -> str | None:
    cleaned = lower_line.strip(" :\t")
    for section_key, variants in JD_SECTION_HEADINGS.items():
        if cleaned in variants:
            return section_key
    return None


def _split_jd_sections(lines: list[str]) -> dict[str, str]:
    sections: dict[str, list[str]] = {key: [] for key in JD_SECTION_HEADINGS}
    current_section = None

    for line in lines:
        lower = line.strip().lower()
        heading_match = _matches_jd_heading(lower)
        if heading_match:
            current_section = heading_match
            continue
        if current_section:
            sections[current_section].append(line)

    return {key: "\n".join(value).strip() for key, value in sections.items()}


def _bullets_to_list(block: str) -> list[str]:
    """Turn a raw section block into a list of cleaned bullet/line strings."""
    if not block:
        return []
    items = []
    for line in block.splitlines():
        cleaned = BULLET_PREFIX_PATTERN.sub("", line.strip())
        if cleaned:
            items.append(cleaned)
    return items


# ---------------------------------------------------------------------------
# Fallback parsing for plain-paragraph job descriptions (no section headings)
# ---------------------------------------------------------------------------

# Explicit "job title" phrases, checked first against the first line, then
# (only if needed) against the whole text.
JOB_TITLE_PATTERNS = [
    re.compile(r"looking for (?:a |an )?(.+?)[.\n]", re.IGNORECASE),
    re.compile(r"hiring\s*:?\s*(.+?)[.\n]", re.IGNORECASE),
    re.compile(r"position\s*:?\s*(.+?)[.\n]", re.IGNORECASE),
]

SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")

# Phrases that signal a sentence is describing REQUIRED skills.
REQUIRED_PHRASES = [
    "should have experience with",
    "candidate should have",
    "must have",
    "requires",
    "required",
    "experience with",
]

# Phrases that signal a sentence is describing PREFERRED (nice-to-have)
# skills. Checked BEFORE REQUIRED_PHRASES, so a sentence like "Experience
# with X is a plus" is classified as preferred, not required, even though
# it also contains "experience with".
PREFERRED_PHRASES = [
    "is a plus",
    "nice to have",
    "nice-to-have",
    "preferred",
    "bonus",
    "plus",
]


def _guess_job_title(lines: list[str], full_text: str) -> str | None:
    """
    1. Check explicit phrases like "We are looking for a ... Developer.",
       "Hiring: ...", or "Position: ..." against the FIRST non-empty line
       first — this is where such a phrase most reliably names just the
       title, without also pulling in a later, unrelated sentence.
    2. If the first line is short and has no such phrase, it's likely
       already just the title (e.g. a heading line above a structured JD) —
       use it as-is.
    3. If the first line is a long paragraph with no explicit phrase in it,
       check the whole text for one of these phrases (it may appear later).
    4. If nothing matches, use the first sentence of that paragraph instead
       of giving up and returning None.
    """
    first_nonempty = None
    for line in lines:
        stripped = line.strip()
        if stripped:
            first_nonempty = stripped
            break

    if first_nonempty is None:
        return None

    for pattern in JOB_TITLE_PATTERNS:
        match = pattern.search(first_nonempty)
        if match:
            candidate = match.group(1).strip().strip(":,")
            if candidate:
                return candidate

    if len(first_nonempty) <= 100:
        return first_nonempty

    for pattern in JOB_TITLE_PATTERNS:
        match = pattern.search(full_text)
        if match:
            candidate = match.group(1).strip().strip(":,")
            if candidate:
                return candidate

    first_sentence = SENTENCE_SPLIT_PATTERN.split(first_nonempty, maxsplit=1)[0].strip()
    return first_sentence if first_sentence else first_nonempty[:100].strip()


def _extract_experience_requirements(text: str) -> list[str]:
    """
    Find lines anywhere in the job description that mention a
    years-of-experience requirement (e.g. "3+ years of experience").
    """
    found = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if EXPERIENCE_PATTERN.search(stripped):
            cleaned = BULLET_PREFIX_PATTERN.sub("", stripped)
            if cleaned not in found:
                found.append(cleaned)
    return found


def _extract_skills_from_sentences(text: str) -> tuple[list[str], list[str]]:
    """
    Fallback for plain-paragraph job descriptions with no recognizable
    section headings: scan sentence by sentence. A sentence matching a
    PREFERRED phrase (checked first) contributes its skills to preferred;
    otherwise, a sentence matching a REQUIRED phrase contributes its skills
    to required. A sentence matching neither is ignored, so we don't just
    dump every skill mentioned anywhere into required_skills.
    """
    sentences = SENTENCE_SPLIT_PATTERN.split(text)

    required_found: dict[str, int] = {}
    preferred_found: dict[str, int] = {}

    for position, sentence in enumerate(sentences):
        lower = sentence.lower()
        skills_here = _find_known_skills(sentence)
        if not skills_here:
            continue

        if any(phrase in lower for phrase in PREFERRED_PHRASES):
            for skill in skills_here:
                if skill not in preferred_found:
                    preferred_found[skill] = position
        elif any(phrase in lower for phrase in REQUIRED_PHRASES):
            for skill in skills_here:
                if skill not in required_found:
                    required_found[skill] = position

    required = [name for name, _ in sorted(required_found.items(), key=lambda kv: kv[1])]
    preferred = [name for name, _ in sorted(preferred_found.items(), key=lambda kv: kv[1])]
    return required, preferred


def analyze_job_description(job_description: str) -> dict:
    """
    Convert raw job description text into a structured dict:
    job_title, required_skills, preferred_skills, responsibilities,
    qualifications, experience_requirements.

    Supports two styles:
    1. Structured JDs with recognizable section headings (Requirements,
       Preferred, Responsibilities, Qualifications) — parsed first.
    2. Plain-paragraph JDs with no headings — for whichever of
       required_skills/preferred_skills came back empty from heading-based
       parsing, a sentence-level fallback looks for common requirement-
       signaling phrases (see REQUIRED_PHRASES/PREFERRED_PHRASES).

    Still rule-based: relies on a fixed skill vocabulary and a fixed set of
    trigger phrases, so it won't catch every possible phrasing or skill.
    """
    lines = job_description.splitlines()
    sections = _split_jd_sections(lines)

    required_skills = _find_known_skills(sections["required_skills"])
    preferred_skills = _find_known_skills(sections["preferred_skills"])

    if not required_skills or not preferred_skills:
        fallback_required, fallback_preferred = _extract_skills_from_sentences(
            job_description
        )
        if not required_skills:
            required_skills = fallback_required
        if not preferred_skills:
            preferred_skills = fallback_preferred

    return {
        "job_title": _guess_job_title(lines, job_description),
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "responsibilities": _bullets_to_list(sections["responsibilities"]),
        "qualifications": _bullets_to_list(sections["qualifications"]),
        "experience_requirements": _extract_experience_requirements(job_description),
    }


def match_resume_to_job(resume_data: dict, job_data: dict) -> dict:
    """
    Compare structured resume data (from resume_analyzer.analyze_resume)
    against structured job data (from analyze_job_description above).

    SCORING FORMULA:
        match_score = round(matched_required_skills / total_required_skills * 100)
    If total_required_skills is 0, match_score is returned as None (not 0),
    since a 0% score would misleadingly imply "no skills matched" rather
    than "no requirements could be detected to check against."

    This does not use any AI/ML prediction — it's a plain, reproducible
    calculation from the two input dicts.
    """
    required_skills = job_data.get("required_skills", [])
    preferred_skills = job_data.get("preferred_skills", [])
    combined_job_skills = set(required_skills) | set(preferred_skills)

    resume_skills_raw = resume_data.get("skills", [])
    normalized_resume_skills = {_normalize_skill(s) for s in resume_skills_raw}

    matched_skills = [s for s in required_skills if s in normalized_resume_skills]
    missing_skills = [s for s in required_skills if s not in normalized_resume_skills]

    total_required = len(required_skills)
    if total_required == 0:
        match_score = None
    else:
        match_score = round(len(matched_skills) / total_required * 100)

    # --- Relevant projects: overlap between a project's technologies and
    # the job's required/preferred skills.
    relevant_projects = []
    for project in resume_data.get("projects", []):
        technologies = project.get("technologies", []) or []
        normalized_tech = {_normalize_skill(t) for t in technologies}
        if normalized_tech & combined_job_skills:
            name = project.get("name") or "Unnamed project"
            relevant_projects.append(name)

    # --- Relevant experience: raw experience text blocks that mention a
    # required/preferred skill.
    relevant_experience = []
    for block in resume_data.get("experience", []):
        if not isinstance(block, str):
            continue
        skills_in_block = set(_find_known_skills(block))
        if skills_in_block & combined_job_skills:
            relevant_experience.append(block)

    # --- Summary
    if total_required == 0:
        summary = (
            "No clearly required skills were detected in the job description, "
            "so a percentage match score could not be calculated."
        )
    else:
        summary = (
            f"The resume matches {len(matched_skills)} of {total_required} "
            f"required skill(s) ({match_score}%)."
        )
        if missing_skills:
            summary += f" Missing: {', '.join(missing_skills)}."
        else:
            summary += " All required skills were found."

    return {
        "match_score": match_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "relevant_projects": relevant_projects,
        "relevant_experience": relevant_experience,
        "summary": summary,
    }