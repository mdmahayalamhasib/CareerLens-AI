"""
Structured information extraction from resume text.
Rule-based (regex + heading detection) for this first version.
Designed to be upgraded later with NLP/LLM without changing its
input/output shape: takes plain text in, returns a dict out.
"""

import re


# Section headings we recognize, mapped to the key we'll use in the output dict.
# Lowercased for matching. Add more variants here as you encounter them.
SECTION_HEADINGS = {
    "skills": ["skills", "technical skills", "core skills", "key skills"],
    "education": ["education", "academic background", "educational background"],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
    ],
    "projects": ["projects", "academic projects", "personal projects"],
    "certifications": ["certifications", "certificates", "licenses & certifications"],
    "leadership": [
        "leadership and volunteering",
        "leadership & volunteering",
        "leadership",
        "volunteering",
    ],
}

EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

PHONE_PATTERN = re.compile(
    r"(\+?\d{1,3}[\s.-]?)?(\(?\d{2,4}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{3,4}"
)

LINKEDIN_PATTERN = re.compile(r"(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9\-_%]+")

GITHUB_PATTERN = re.compile(r"(https?://)?(www\.)?github\.com/[A-Za-z0-9\-_%]+")

# A simple "City, Country" or "City, State" shape — used only on lines that
# already contain an email or phone number (i.e. the contact-info line).
LOCATION_PATTERN = re.compile(r"^[A-Za-z][A-Za-z\s]+,\s*[A-Za-z][A-Za-z\s]+$")

# Matches a short "Label:" prefix at the start of a line, e.g. "Languages:",
# "Web and Databases:", "Tools and Testing:", "ML and APIs:".
SKILL_CATEGORY_PREFIX_PATTERN = re.compile(r"^[A-Za-z][A-Za-z\s&/-]{0,40}:\s*")

# A line that is ONLY a year or year-range, nothing else — used as the
# structural signal for "a new project starts here" (title is always
# immediately followed by a line like this).
STANDALONE_YEAR_PATTERN = re.compile(
    r"^\d{4}(\s*[-–]\s*(?:\d{4}|present))?$", re.IGNORECASE
)

BULLET_PREFIX_PATTERN = re.compile(r"^[•▪◦·*-]\s*")


def _extract_email(text: str) -> str | None:
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else None


def _extract_phone(text: str) -> str | None:
    match = PHONE_PATTERN.search(text)
    if not match:
        return None
    candidate = match.group(0).strip()
    digit_count = len(re.sub(r"\D", "", candidate))
    if digit_count < 7:
        return None
    return candidate


def _extract_linkedin(text: str) -> str | None:
    match = LINKEDIN_PATTERN.search(text)
    return match.group(0) if match else None


def _extract_github(text: str) -> str | None:
    match = GITHUB_PATTERN.search(text)
    return match.group(0) if match else None


def _extract_location(text: str) -> str | None:
    """
    Look only at lines that already contain an email or phone number
    (the contact-info line), split that line into segments, and return
    the first segment that looks like "City, Country" and isn't itself
    an email/phone/URL. Deliberately conservative to avoid false matches
    elsewhere in the document.
    """
    for line in text.splitlines():
        if not (EMAIL_PATTERN.search(line) or PHONE_PATTERN.search(line)):
            continue

        segments = re.split(r"[|•]", line)
        for segment in segments:
            candidate = segment.strip()
            if not candidate:
                continue
            if EMAIL_PATTERN.search(candidate):
                continue
            if "http" in candidate.lower():
                continue
            digit_count = len(re.sub(r"\D", "", candidate))
            if digit_count >= 7:
                continue  # this segment is the phone number, not a location
            if len(candidate) <= 60 and LOCATION_PATTERN.match(candidate):
                return candidate
    return None


def _guess_name(lines: list[str]) -> str | None:
    """
    Very simple heuristic: the first non-empty line, unless it looks like
    an email, phone number, URL, or a known section heading.
    This is the least reliable field in this module.
    """
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()
        if EMAIL_PATTERN.search(stripped):
            continue
        if PHONE_PATTERN.search(stripped) and len(re.sub(r"\D", "", stripped)) >= 7:
            continue
        if "http" in lower or "linkedin.com" in lower or "github.com" in lower:
            continue
        if _matches_any_heading(lower):
            continue
        if len(stripped) <= 60:
            return stripped
    return None


def _matches_any_heading(lower_line: str) -> str | None:
    """Return the section key if lower_line looks like one of our known headings."""
    cleaned = lower_line.strip(" :\t")
    for section_key, variants in SECTION_HEADINGS.items():
        if cleaned in variants:
            return section_key
    return None


def _split_into_sections(lines: list[str]) -> dict[str, str]:
    """
    Walk through the lines, detect heading lines, and group everything
    after a heading (until the next heading) as that section's raw text.
    """
    sections: dict[str, list[str]] = {key: [] for key in SECTION_HEADINGS}
    current_section = None

    for line in lines:
        lower = line.strip().lower()
        heading_match = _matches_any_heading(lower)

        if heading_match:
            current_section = heading_match
            continue  # don't include the heading line itself in the content

        if current_section:
            sections[current_section].append(line)

    return {key: "\n".join(value).strip() for key, value in sections.items()}


def _split_skills_list(skills_block: str) -> list[str]:
    """
    Turn the raw 'skills' section text into a flat list of individual skills.
    Strips leading category labels per line (e.g. "Languages:", "Tools and
    Testing:") before splitting on commas/bullets/newlines.
    """
    if not skills_block:
        return []

    all_skills: list[str] = []

    for line in skills_block.splitlines():
        line = SKILL_CATEGORY_PREFIX_PATTERN.sub("", line.strip())
        normalized = re.sub(r"[•▪◦·]", ",", line)
        for item in re.split(r"[,\n]", normalized):
            cleaned = item.strip(" -\t")
            if cleaned:
                all_skills.append(cleaned)

    return all_skills


def _is_new_title_start(lines: list[str], idx: int) -> bool:
    """
    Structural signal for "a new project begins at lines[idx]": true only if
    this line is not a bullet, AND the next non-empty line is a standalone
    year (matching the title -> year -> tech -> description pattern).
    This deliberately ignores commas/pipes in the line itself, so a
    technology/metadata line is never mistaken for a title.
    """
    line = lines[idx].strip()
    if not line or BULLET_PREFIX_PATTERN.match(line):
        return False

    j = idx + 1
    while j < len(lines) and lines[j].strip() == "":
        j += 1

    return j < len(lines) and bool(STANDALONE_YEAR_PATTERN.fullmatch(lines[j].strip()))


def _parse_projects(projects_block: str) -> list[dict]:
    """
    Convert the raw 'projects' section text into a list of individual
    project dicts, following the structural pattern:
        title -> (optional) standalone year -> (optional) tech/metadata line -> bullets -> next title
    A new project is only recognized via that structure (title immediately
    followed by a standalone year), never by line content like commas or '|'.
    """
    if not projects_block:
        return []

    lines = projects_block.splitlines()
    n = len(lines)
    projects: list[dict] = []
    i = 0

    while i < n and lines[i].strip() == "":
        i += 1

    while i < n:
        title_line = lines[i].strip()
        i += 1

        year = None
        technologies: list[str] = []
        description_lines: list[str] = []

        while i < n and lines[i].strip() == "":
            i += 1

        # Requirement 2: a standalone year right after the title is the project's year.
        if i < n and STANDALONE_YEAR_PATTERN.fullmatch(lines[i].strip()):
            year = lines[i].strip()
            i += 1

            while i < n and lines[i].strip() == "":
                i += 1

            # Requirement 3: the line immediately after the year is the tech/metadata
            # line, not a new project — regardless of its content.
            if i < n and not BULLET_PREFIX_PATTERN.match(lines[i].strip()):
                tech_line = lines[i].strip()
                # Requirement 4: strip trailing "| GitHub | Live Demo"-style metadata.
                tech_part = tech_line.split("|")[0]
                # Requirement 5: parse what's left as comma-separated technologies.
                technologies = [t.strip() for t in tech_part.split(",") if t.strip()]
                i += 1

        # Requirements 6-7: collect bullets/description until the next project title.
        while i < n:
            if lines[i].strip() == "":
                i += 1
                continue
            if _is_new_title_start(lines, i):
                break
            cleaned = BULLET_PREFIX_PATTERN.sub("", lines[i].strip())
            if cleaned:
                description_lines.append(cleaned)
            i += 1

        projects.append(
            {
                "name": title_line if title_line else None,
                "year": year,
                "technologies": technologies,
                "description": "\n".join(description_lines).strip(),
            }
        )

    return projects


def analyze_resume(text: str) -> dict:
    """
    Convert raw resume text into a structured dict.
    This is intentionally rule-based and will not perfectly parse every
    resume layout — see module docstring for known limits.
    """
    lines = text.splitlines()

    sections = _split_into_sections(lines)

    return {
        "name": _guess_name(lines),
        "email": _extract_email(text),
        "phone": _extract_phone(text),
        "location": _extract_location(text),
        "linkedin": _extract_linkedin(text),
        "github": _extract_github(text),
        "skills": _split_skills_list(sections["skills"]),
        "education": [sections["education"]] if sections["education"] else [],
        "experience": [sections["experience"]] if sections["experience"] else [],
        "projects": _parse_projects(sections["projects"]),
        "certifications": (
            [sections["certifications"]] if sections["certifications"] else []
        ),
        "leadership": [sections["leadership"]] if sections["leadership"] else [],
    }