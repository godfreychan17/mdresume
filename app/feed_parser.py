"""Parse feed.md into a Resume model.

feed.md format
--------------
YAML front matter (between --- delimiters) declares meta, layout, sections_order.
The body uses Markdown headings to delineate sections:

  # Header          <- key: value pairs
  ## Summary        <- free text paragraph
  ## Experience     <- ### Role @ Company | dates, then bullet list
  ## Education      <- ### Degree @ Institution | dates, then detail list
  ## Skills         <- key: value pairs (comma-separated values)
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from app.models import (
    EducationEntry,
    ExperienceEntry,
    Resume,
    ResumeHeader,
    ResumeLayout,
    ResumeMeta,
)


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Return (front_matter_dict, body_text)."""
    stripped = text.strip()
    if not stripped.startswith("---"):
        return {}, stripped

    parts = re.split(r"^---\s*$", stripped, maxsplit=2, flags=re.MULTILINE)
    if len(parts) < 3:
        return {}, stripped

    fm = yaml.safe_load(parts[1]) or {}
    return fm, parts[2].strip()


def _parse_kv_block(text: str) -> dict[str, str]:
    """Parse 'key: value' lines into a dict, skipping blanks and non-kv lines."""
    result: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()
    return result


def _parse_header_block(text: str) -> ResumeHeader:
    kv = _parse_kv_block(text)
    return ResumeHeader(
        name=kv.get("name", ""),
        title=kv.get("title", ""),
        email=kv.get("email", ""),
        phone=kv.get("phone"),
        location=kv.get("location"),
        linkedin=kv.get("linkedin"),
        github=kv.get("github"),
        website=kv.get("website"),
    )


def _parse_experience_block(text: str) -> list[ExperienceEntry]:
    entries: list[ExperienceEntry] = []
    # Split on ### headings
    chunks = re.split(r"^###\s+", text, flags=re.MULTILINE)
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = chunk.splitlines()
        heading = lines[0].strip()
        rest = "\n".join(lines[1:])

        # "Role @ Company | dates"
        match = re.match(r"^(.+?)\s+@\s+(.+?)\s*\|\s*(.+)$", heading)
        if not match:
            continue
        role, company, dates = match.group(1).strip(), match.group(2).strip(), match.group(3).strip()

        bullets = [
            line.lstrip("-• ").strip()
            for line in rest.splitlines()
            if line.strip().startswith(("-", "•"))
        ]
        entries.append(ExperienceEntry(role=role, company=company, dates=dates, bullets=bullets))
    return entries


def _parse_education_block(text: str) -> list[EducationEntry]:
    entries: list[EducationEntry] = []
    chunks = re.split(r"^###\s+", text, flags=re.MULTILINE)
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        lines = chunk.splitlines()
        heading = lines[0].strip()
        rest = "\n".join(lines[1:])

        match = re.match(r"^(.+?)\s+@\s+(.+?)\s*\|\s*(.+)$", heading)
        if not match:
            continue
        degree, institution, dates = match.group(1).strip(), match.group(2).strip(), match.group(3).strip()

        details = [
            line.lstrip("-• ").strip()
            for line in rest.splitlines()
            if line.strip().startswith(("-", "•"))
        ]
        entries.append(EducationEntry(degree=degree, institution=institution, dates=dates, details=details))
    return entries


def _parse_skills_block(text: str) -> dict[str, str]:
    """Returns {category: 'comma, separated, items'}."""
    return _parse_kv_block(text)


def _section_body(sections: dict[str, str], name: str) -> str:
    return sections.get(name, "").strip()


def parse_feed(path: str | Path) -> Resume:
    text = Path(path).read_text(encoding="utf-8")
    fm, body = _split_frontmatter(text)

    meta_raw = fm.get("meta", {})
    layout_raw = fm.get("layout", {})
    sections_order: list[str] = fm.get("sections_order", ["header", "summary", "experience", "education", "skills"])

    meta = ResumeMeta(
        page=meta_raw.get("page", "A4"),
        theme=meta_raw.get("theme", "classic"),
    )
    layout = ResumeLayout(
        columns=layout_raw.get("columns", 1),
        margins_mm=layout_raw.get("margins_mm", [15, 20, 15, 20]),
    )

    # Split body into named sections by h2 headings
    sections: dict[str, str] = {}
    # The very first block before any ## is the Header block (under # Header)
    raw_body = body
    # Remove top-level h1 heading (# Header) and treat its content as header section
    raw_body = re.sub(r"^#\s+\S.*$", "", raw_body, flags=re.MULTILINE)

    parts = re.split(r"^##\s+(.+)$", raw_body, flags=re.MULTILINE)
    # parts[0] is text before first ##, then alternating name/content
    # Text before first ## could contain header kv pairs
    preamble = parts[0]
    if preamble.strip():
        sections["header"] = preamble

    for i in range(1, len(parts) - 1, 2):
        section_name = parts[i].strip().lower()
        section_content = parts[i + 1]
        sections[section_name] = section_content

    header = _parse_header_block(_section_body(sections, "header"))
    summary = _section_body(sections, "summary") or None
    experience = _parse_experience_block(_section_body(sections, "experience"))
    education = _parse_education_block(_section_body(sections, "education"))
    skills = _parse_skills_block(_section_body(sections, "skills"))

    return Resume(
        meta=meta,
        layout=layout,
        sections_order=sections_order,
        header=header,
        summary=summary,
        experience=experience,
        education=education,
        skills=skills,
    )


def resume_to_feed(resume: Resume) -> str:
    """Serialise a Resume model back to feed.md text."""
    fm: dict[str, Any] = {
        "meta": {"page": resume.meta.page, "theme": resume.meta.theme},
        "layout": {
            "columns": resume.layout.columns,
            "margins_mm": resume.layout.margins_mm,
        },
        "sections_order": resume.sections_order,
    }
    lines = ["---", yaml.dump(fm, default_flow_style=False).rstrip(), "---", ""]

    lines += ["# Header"]
    h = resume.header
    for field, value in [
        ("name", h.name),
        ("title", h.title),
        ("email", h.email),
        ("phone", h.phone),
        ("location", h.location),
        ("linkedin", h.linkedin),
        ("github", h.github),
        ("website", h.website),
    ]:
        if value:
            lines.append(f"{field}: {value}")

    if resume.summary:
        lines += ["", "## Summary", resume.summary]

    if resume.experience:
        lines += ["", "## Experience"]
        for exp in resume.experience:
            lines.append(f"\n### {exp.role} @ {exp.company} | {exp.dates}")
            for b in exp.bullets:
                lines.append(f"- {b}")

    if resume.education:
        lines += ["", "## Education"]
        for edu in resume.education:
            lines.append(f"\n### {edu.degree} @ {edu.institution} | {edu.dates}")
            for d in edu.details:
                lines.append(f"- {d}")

    if resume.skills:
        lines += ["", "## Skills"]
        for cat, vals in resume.skills.items():
            lines.append(f"{cat}: {vals}")

    return "\n".join(lines) + "\n"
