"""Export a Resume to a dated PDF using WeasyPrint."""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from app.models import Resume
from app.renderer import render_resume_html


def export_pdf(
    resume: Resume,
    out_dir: str | Path = "output",
    filename: str | None = None,
) -> Path:
    """Render resume to PDF and return the output path.

    Parameters
    ----------
    resume:   Parsed Resume model.
    out_dir:  Directory for the output file (created if absent).
    filename: Override the default YYYY-MM-DD_resume.pdf name.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        today = date.today().strftime("%Y-%m-%d")
        safe_name = re.sub(r"[^\w]+", "_", resume.header.name.lower()).strip("_")
        filename = f"{today}_{safe_name}_resume.pdf"

    out_path = out_dir / filename

    html_str = render_resume_html(resume, edit_mode=False)
    font_config = FontConfiguration()
    HTML(string=html_str, base_url=str(Path(__file__).parent.parent)).write_pdf(
        str(out_path),
        font_config=font_config,
    )
    return out_path
