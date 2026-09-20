"""Extract layout hints from template.pdf and merge into Resume.

What we read
------------
- Page size (to set the @page CSS rule and feed.md meta.page)
- Approximate content margins (by finding the bounding box of text on page 1)

These become defaults only; feed.md layout values always win.
"""
from __future__ import annotations

from pathlib import Path

from app.models import Resume


def _mm(pts: float) -> int:
    """Convert PDF points to millimetres (rounded)."""
    return round(pts * 25.4 / 72)


def _extract_hints(pdf_path: Path) -> dict:
    """Return {'page': str, 'margins_mm': [top, right, bottom, left]} or {}."""
    try:
        import pdfplumber  # optional dependency
    except ImportError:
        return {}

    try:
        with pdfplumber.open(str(pdf_path)) as pdf:
            if not pdf.pages:
                return {}
            page = pdf.pages[0]
            pw_pts = page.width
            ph_pts = page.height

            # Determine page size name
            pw_mm = _mm(pw_pts)
            ph_mm = _mm(ph_pts)
            if 207 <= pw_mm <= 213 and 294 <= ph_mm <= 300:
                page_name = "A4"
            elif 209 <= pw_mm <= 219 and 274 <= ph_mm <= 284:
                page_name = "Letter"
            else:
                page_name = f"{pw_mm}x{ph_mm}mm"

            # Find text bounding box → infer margins
            words = page.extract_words()
            if not words:
                return {"page": page_name}

            xs = [float(w["x0"]) for w in words] + [float(w["x1"]) for w in words]
            ys = [float(w["top"]) for w in words] + [float(w["bottom"]) for w in words]

            left_pts   = min(xs)
            right_pts  = pw_pts - max(xs)
            top_pts    = min(ys)
            bottom_pts = ph_pts - max(ys)

            margins = [
                max(5, _mm(top_pts)),
                max(5, _mm(right_pts)),
                max(5, _mm(bottom_pts)),
                max(5, _mm(left_pts)),
            ]
            return {"page": page_name, "margins_mm": margins}

    except Exception:
        return {}


def apply_template_layout(resume: Resume, pdf_path: str | Path) -> Resume:
    """Merge layout hints from template.pdf into resume (feed.md values win).

    Returns the mutated resume (same object).
    """
    hints = _extract_hints(Path(pdf_path))
    if not hints:
        return resume

    # page: only set if feed.md left it at the default "A4" literally
    if hints.get("page") and resume.meta.page == "A4":
        resume.meta.page = hints["page"]

    # margins: only fill in if feed.md has the exact default [15, 20, 15, 20]
    default_margins = [15, 20, 15, 20]
    if hints.get("margins_mm") and resume.layout.margins_mm == default_margins:
        resume.layout.margins_mm = hints["margins_mm"]

    return resume
