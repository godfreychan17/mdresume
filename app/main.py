"""FastAPI app — preview, text-edit, and PDF export."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.feed_parser import parse_feed, resume_to_feed
from app.models import Resume
from app.pdf_export import export_pdf
from app.renderer import render_resume_html
from app.template_layout import apply_template_layout

BASE_DIR     = Path(__file__).parent.parent
FEED_PATH    = BASE_DIR / "feed.md"
TEMPLATE_PDF = BASE_DIR / "template.pdf"
OUTPUT_DIR   = BASE_DIR / "output"

app = FastAPI(title="mdresume")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


def _load_resume() -> Resume:
    if not FEED_PATH.exists():
        raise HTTPException(status_code=404, detail="feed.md not found")
    resume = parse_feed(FEED_PATH)
    if TEMPLATE_PDF.exists():
        resume = apply_template_layout(resume, TEMPLATE_PDF)
    return resume


# ── Routes ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def preview():
    """Serve the editable HTML preview."""
    resume = _load_resume()
    return render_resume_html(resume, edit_mode=True)


@app.get("/print", response_class=HTMLResponse)
def print_view():
    """Plain printable HTML (no editor chrome)."""
    resume = _load_resume()
    return render_resume_html(resume, edit_mode=False)


class ContentPayload(BaseModel):
    fields: dict[str, Any]


@app.post("/api/content")
def save_content(payload: ContentPayload):
    """Patch edited field values back into feed.md.

    Each key in payload.fields is a dot-notation field path, e.g.
      'header.name', 'experience.0.role', 'skills.languages'
    Values are plain strings (text-only edits from the browser).
    """
    resume = _load_resume()

    for field_path, value in payload.fields.items():
        value = str(value).strip()
        parts = field_path.split(".")

        try:
            if parts[0] == "header" and len(parts) == 2:
                setattr(resume.header, parts[1], value)

            elif parts[0] == "summary":
                resume.summary = value

            elif parts[0] == "experience" and len(parts) >= 3:
                idx = int(parts[1])
                if idx >= len(resume.experience):
                    continue
                entry = resume.experience[idx]
                if parts[2] == "role":
                    entry.role = value
                elif parts[2] == "company":
                    entry.company = value
                elif parts[2] == "dates":
                    entry.dates = value
                elif parts[2] == "bullets" and len(parts) == 4:
                    bidx = int(parts[3])
                    if bidx < len(entry.bullets):
                        entry.bullets[bidx] = value

            elif parts[0] == "education" and len(parts) >= 3:
                idx = int(parts[1])
                if idx >= len(resume.education):
                    continue
                entry = resume.education[idx]
                if parts[2] == "degree":
                    entry.degree = value
                elif parts[2] == "institution":
                    entry.institution = value
                elif parts[2] == "dates":
                    entry.dates = value
                elif parts[2] == "details" and len(parts) == 4:
                    didx = int(parts[3])
                    if didx < len(entry.details):
                        entry.details[didx] = value

            elif parts[0] == "skills" and len(parts) == 2:
                resume.skills[parts[1]] = value

        except (IndexError, ValueError, AttributeError):
            continue

    FEED_PATH.write_text(resume_to_feed(resume), encoding="utf-8")
    return {"ok": True}


@app.post("/api/export")
def export():
    """Generate a dated PDF and stream it to the browser."""
    resume = _load_resume()
    out_path = export_pdf(resume, out_dir=OUTPUT_DIR)
    return FileResponse(
        path=str(out_path),
        media_type="application/pdf",
        filename=out_path.name,
        headers={"X-Filename": out_path.name},
    )
