"""Render a Resume model to an HTML string via Jinja2."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.models import Resume

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
_STATIC_DIR = Path(__file__).parent.parent / "static"

_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)


def render_resume_html(resume: Resume, *, edit_mode: bool = False) -> str:
    """Return the full HTML string for the resume.

    When edit_mode=True the preview wrapper is used (toolbar + contenteditable).
    When edit_mode=False the plain printable template is used.
    """
    css = (_STATIC_DIR / "resume.css").read_text(encoding="utf-8")
    template_name = "preview.html" if edit_mode else "resume.html"
    tmpl = _env.get_template(template_name)
    return tmpl.render(resume=resume, css=css)
