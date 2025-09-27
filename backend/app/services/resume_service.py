import re
import string
from typing import Dict, List

from fastapi import HTTPException
from app.utils.pdf.pdf_utils import extract_pdf_content
from app.models.schema.fastapi.db_collections import Collections
from app.models.db.resume_parsed import ParsedResumeDB

# Canonical section groups. Keep lowercase terms only.
SECTION_HEADINGS = [
    ["skill", "technologies", "technology", "tool"],
    ["experience", "work history", "employment", "career"],
    ["project"],
    ["education", "academics", "qualification", "degree"],
    ["achievement", "accomplishment", "award", "honor", "recognition"],
    ["certification", "license", "course", "training"],
    ["summary", "profile", "objective", "about", "introduction"],
    ["competition", "competitive", "hackathon", "coding contests", "challenges"],
]


def normalize_line(line: str) -> str:
    # Remove punctuation
    table = str.maketrans("", "", string.punctuation)
    no_punct = line.translate(table)
    normalized = " ".join(no_punct.lower().split())
    return normalized


def is_heading(line: str, section_keywords: list[list[str]]) -> str | None:
    normalized_line = normalize_line(line)
    words = normalized_line.strip().split()
    if len(words) <= 4:  # allow slightly longer heading like "technical skills"
        for group in section_keywords:
            for kw in group:
                if any(word.startswith(kw) for word in words):
                    return group[0]
    return None


def detect_sections(resume_text: str) -> Dict[str, List[str]]:
    sections: Dict[str, List[str]] = {}
    # Keep blank lines as separators but trim whitespace
    lines = [line.rstrip() for line in resume_text.splitlines()]

    current_section = "unknown"
    buffer: List[str] = []

    for line in lines:
        if not line.strip():
            # blank line — keep as is but it also helps separate blocks
            if buffer:
                sections.setdefault(current_section, []).append(
                    "\n".join(buffer).strip()
                )
                buffer = []
            continue

        heading_match = is_heading(line, SECTION_HEADINGS)
        if heading_match:
            if buffer:
                sections.setdefault(current_section, []).append(
                    "\n".join(buffer).strip()
                )
                buffer = []
            current_section = heading_match
            continue

        buffer.append(line)

    if buffer:
        sections.setdefault(current_section, []).append("\n".join(buffer).strip())

    return sections


def clean_skills(skills_text: List[str] | str) -> List[str]:
    if isinstance(skills_text, list):
        text = "\n".join(skills_text)
    else:
        text = skills_text

    # split on common delimiters including colon as requested
    raw_skills = re.split(r"[,;:\n\u2022•]", text)
    skills = [s.strip().lower() for s in raw_skills if s.strip()]
    return skills


def parse_resume_bytes(data: bytes) -> Dict[str, List[str]]:
    raw_text, links = extract_pdf_content(data)
    sections = detect_sections(raw_text)

    parsed_resume = {"links": links}
    for sec, content in sections.items():
        if sec == "skill":
            parsed_resume[sec] = clean_skills(content)
        else:
            parsed_resume[sec] = [line.strip() for line in content if line.strip()]

    return parsed_resume


def get_sections_from_resume(data: bytes) -> Dict[str, List[str]]:
    parsed = parse_resume_bytes(data)
    sections = {k: v for k, v in parsed.items()}

    return sections


async def insert_parsed_resume(
    resume_id: str, owner_id: str, workspace_id: str, sections, collections: Collections
):
    _ = await collections.resume_parsed.insert_one(
        ParsedResumeDB(
            file_id=resume_id,
            owner_id=owner_id,
            workspace_id=workspace_id,
            sections=sections,
        ).model_dump()
    )


async def is_resume_parsed(resume_id: str, collections: Collections):
    already_parsed = await collections.resume_parsed.find_one({"file_id": resume_id})

    if already_parsed:
        raise HTTPException(
            status_code=400,
            detail="This resume has already been parsed",
        )
