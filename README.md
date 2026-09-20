# mdresume

A Python tool that converts a structured `feed.md` file into an interactive HTML preview and a dated PDF resume.

## Flow

```
guideline.md + template.pdf (optional)
         │
         ▼
   AI chat with human
         │
         ▼
      feed.md
         │
         ▼
  Python app (FastAPI)
         │
    ┌────┴─────┐
    ▼           ▼
Website     YYYY-MM-DD
preview    _resume.pdf
(edit text)
```

## Setup

**Requirements:** Python 3.11 or 3.12 (recommended).
> Python 3.13+ is not yet supported by all dependencies — use 3.12 if available.

```bash
# 1. Create a virtual environment with Python 3.12
python3.12 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (macOS) WeasyPrint needs Pango — install via Homebrew if missing
brew install pango
```

## Usage

### Web preview + editor

```bash
uvicorn app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

- Click any text on the resume to edit it in place.
- **Save changes** — writes edits back to `feed.md`.
- **Export PDF** — downloads `YYYY-MM-DD_<name>_resume.pdf`.

### Headless PDF export (CLI)

```bash
python -m app export
# with options:
python -m app export --feed feed.md --out output/ --filename my_resume.pdf
```

## Adding your own resume

1. Read `guideline.md` (or give it to an AI assistant).
2. Chat with the AI — it will ask for your work history, skills, and contact details.
3. The AI emits a complete `feed.md`. Replace the sample one in this folder.
4. (Optional) Drop a `template.pdf` in the project root to guide layout and page size.
5. Run the web preview or CLI export.

## Using template.pdf

Place any PDF resume template as `template.pdf` in the project root before starting the app.

- **For the AI:** describe the template's layout to the AI during your chat, or share the file directly. The AI will mirror its section order, margins, and density in `feed.md`.
- **For the program:** the app auto-reads the page size and approximate margins from `template.pdf` and uses them as layout defaults (your `feed.md` layout values always take priority).

## File reference

| File | Purpose |
|---|---|
| `guideline.md` | Instructions for an AI to produce `feed.md` |
| `feed.md` | Your resume content and layout config |
| `template.pdf` | Optional layout reference PDF |
| `app/feed_parser.py` | Parses `feed.md` → Python model |
| `app/renderer.py` | Renders model → HTML via Jinja2 |
| `app/pdf_export.py` | HTML → PDF via WeasyPrint |
| `app/template_layout.py` | Extracts layout hints from `template.pdf` |
| `app/main.py` | FastAPI server (preview + save + export) |
| `templates/resume.html` | Printable resume template |
| `templates/preview.html` | Editor chrome (toolbar + contenteditable) |
| `static/resume.css` | Shared print/screen styles |
| `static/editor.js` | In-browser text editing + API calls |
| `output/` | Generated PDFs (git-ignored) |

## feed.md quick reference

```yaml
---
meta:
  page: A4          # A4 | Letter
  theme: classic
layout:
  columns: 1
  margins_mm: [15, 20, 15, 20]   # top right bottom left (mm)
sections_order: [header, summary, experience, education, skills]
---

# Header
name: Your Name
title: Your Title
email: you@email.com
phone: +XX XXXX XXXX
location: City, Country
linkedin: linkedin.com/in/handle
github: github.com/handle

## Summary
Short prose paragraph (40–60 words).

## Experience

### Role @ Company | Month YYYY – Month YYYY
- Bullet (quantified achievement)
- Bullet

## Education

### Degree @ Institution | YYYY – YYYY
- Optional detail

## Skills
category: item1, item2, item3
```

See `guideline.md` for full AI instructions and the complete schema spec.
