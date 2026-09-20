# Project Structure

This document describes every file in the project, its purpose, and the key interfaces an AI needs to know when modifying the codebase.

---

## Directory tree

```
project-root/
├── feed.md                    # Resume content + layout config (AI-generated, human-editable)
├── guideline.md               # Instructions for an AI to produce a valid feed.md
├── template.pdf               # (optional) Drop a PDF here to auto-derive layout defaults
├── requirements.txt           # Python dependencies (pip install -r requirements.txt)
├── README.md                  # Human-facing setup and usage guide
├── STRUCTURE.md               # This file
├── .gitignore
│
├── app/                       # All Python source code
│   ├── __init__.py
│   ├── __main__.py            # CLI entry point  →  python -m app export
│   ├── models.py              # Pydantic data models (Resume, Header, Experience, …)
│   ├── feed_parser.py         # feed.md  →  Resume model  (and back)
│   ├── template_layout.py     # template.pdf  →  layout hints  →  merged into Resume model
│   ├── renderer.py            # Resume model  →  HTML string via Jinja2
│   ├── pdf_export.py          # HTML string  →  WeasyPrint  →  dated PDF file
│   └── main.py                # FastAPI server (preview, save, export endpoints)
│
├── templates/                 # Jinja2 HTML templates
│   ├── resume.html            # Printable-only template (no editor chrome)
│   └── preview.html           # Editor template (toolbar + contenteditable fields)
│
├── static/                    # Browser assets served by FastAPI
│   ├── resume.css             # Shared styles for both screen preview and WeasyPrint PDF
│   └── editor.js              # In-browser text editing, auto-save, PDF download
│
└── output/                    # Generated PDFs land here (git-ignored)
    └── YYYY-MM-DD_name_resume.pdf
```

---

## File-by-file reference

### `feed.md`
The single source of truth for resume content. Written by an AI (guided by `guideline.md`), then optionally hand-edited in the browser or directly.

Format: YAML front matter + Markdown body. See `guideline.md` §3 for the full schema.

Key fields the parser reads:
- `meta.page` — `A4` or `Letter`
- `meta.theme` — `classic` (only value currently)
- `layout.columns` — `1`
- `layout.margins_mm` — `[top, right, bottom, left]` in mm
- `sections_order` — controls render order and visibility
- `# Header` block — `key: value` pairs (name, title, email, phone, location, linkedin, github)
- `## Summary` — plain prose
- `## Experience` — `### Role @ Company | Dates` entries with `- bullet` lists
- `## Education` — `### Degree @ Institution | Dates` entries
- `## Skills` — `category: item1, item2` lines

### `guideline.md`
Read this into any AI chat to make it produce a valid `feed.md`. Covers: interview flow, exact schema rules, template.pdf usage, ATS mode, one-page vs two-page heuristics.

### `template.pdf`
Optional. Drop any PDF resume template here before starting the app. The program reads page size and text bounding box margins from page 1 and uses them as layout defaults (feed.md values always override).

### `requirements.txt`
```
fastapi
uvicorn[standard]
jinja2
weasyprint==61.2
pydyf==0.8.0          # must be pinned — newer pydyf breaks WeasyPrint 61.2
pdfplumber
pypdf
python-multipart
pydantic
pyyaml
markdown
```
Use Python 3.12. Python 3.13+ is not yet supported by all dependencies.

---

## `app/` module details

### `models.py`
Pydantic models — the internal data contract between all modules.

```python
Resume
  .meta        → ResumeMeta(page, theme)
  .layout      → ResumeLayout(columns, margins_mm)
  .sections_order → list[str]
  .header      → ResumeHeader(name, title, email, phone, location, linkedin, github, website)
  .summary     → str | None
  .experience  → list[ExperienceEntry(role, company, dates, bullets)]
  .education   → list[EducationEntry(degree, institution, dates, details)]
  .skills      → dict[str, str]   # {category: "comma, separated, values"}
```

### `feed_parser.py`
Two public functions:

| Function | Signature | Purpose |
|---|---|---|
| `parse_feed` | `(path) → Resume` | Read feed.md, return Resume model |
| `resume_to_feed` | `(Resume) → str` | Serialise Resume back to feed.md text |

Parsing steps:
1. Split YAML front matter from Markdown body (regex on `---` delimiters)
2. Split body on `## heading` lines → `sections` dict
3. Parse each section individually (kv pairs / `### entry` splitting / bullet extraction)

### `template_layout.py`
One public function:

| Function | Signature | Purpose |
|---|---|---|
| `apply_template_layout` | `(resume, pdf_path) → Resume` | Merge PDF layout hints into Resume |

Uses `pdfplumber` to read page 1 word bounding boxes, infers margins in mm, sets `resume.meta.page` and `resume.layout.margins_mm` only if the feed.md values are still at their defaults.

### `renderer.py`
One public function:

| Function | Signature | Purpose |
|---|---|---|
| `render_resume_html` | `(resume, *, edit_mode=False) → str` | Render HTML string |

- `edit_mode=False` → uses `templates/resume.html` (for PDF and `/print` route)
- `edit_mode=True` → uses `templates/preview.html` (for browser editing at `/`)
- Inlines `static/resume.css` directly into the `<style>` tag so WeasyPrint can read it without a live server

### `pdf_export.py`
One public function:

| Function | Signature | Purpose |
|---|---|---|
| `export_pdf` | `(resume, out_dir, filename) → Path` | Write dated PDF, return path |

Default filename: `YYYY-MM-DD_firstname_lastname_resume.pdf`

### `main.py` — FastAPI endpoints

| Method | Path | What it does |
|---|---|---|
| `GET` | `/` | Parse feed.md → render preview.html → return HTML |
| `GET` | `/print` | Parse feed.md → render resume.html → return plain printable HTML |
| `POST` | `/api/content` | Accept `{fields: {dot.path: value}}` → patch Resume → write feed.md |
| `POST` | `/api/export` | Parse feed.md → export PDF → stream as FileResponse download |

`/api/content` field path format:
- `header.name`, `header.email`, … (any ResumeHeader field)
- `summary`
- `experience.0.role`, `experience.0.company`, `experience.0.dates`
- `experience.0.bullets.0`, `experience.0.bullets.1`, …
- `education.0.degree`, `education.0.institution`, `education.0.dates`
- `education.0.details.0`, …
- `skills.languages`, `skills.frameworks`, … (any skill category)

### `__main__.py` — CLI

```bash
python -m app export
python -m app export --feed feed.md --out output/ --filename custom.pdf
```

---

## `templates/` details

Both templates receive `resume` (Resume model) and `css` (contents of resume.css) as Jinja2 context variables.

Every editable value in `preview.html` has two attributes:
- `data-field="dot.path"` — identifies the field for `editor.js` and `/api/content`
- `contenteditable="true"` — enables browser inline editing

`resume.html` has `data-field` but no `contenteditable` (PDF/print use only).

---

## `static/` details

### `resume.css`
- CSS custom properties control margins: `--margin-top`, `--margin-right`, `--margin-bottom`, `--margin-left` (set inline in the template from `resume.layout.margins_mm`)
- `@page { size: A4; margin: 0; }` for WeasyPrint
- `@media print` hides `.editor-toolbar`
- Fonts: EB Garamond (headings/name) + Inter (body text) via Google Fonts import

### `editor.js`
Key behaviours:
- `input` event on any `contenteditable` → marks page dirty, shows "Unsaved changes"
- `focusout` on any `contenteditable` → auto-calls `POST /api/content` with all current field values
- Enter key → prevented (text-only, no line breaks)
- Paste → stripped to plain text via `execCommand('insertText')`
- Export button → saves first, then `POST /api/export` → blob → hidden `<a>` download
- `beforeunload` → warns if unsaved changes exist

---

## Data flow summary

```
feed.md ──parse_feed──► Resume model ──apply_template_layout──► Resume model (with PDF hints)
                                              │
                              ┌───────────────┴────────────────┐
                              ▼                                ▼
                    render(edit_mode=True)          render(edit_mode=False)
                              │                                ▼
                         preview.html                    resume.html
                              │                                ▼
                         FastAPI GET /               WeasyPrint export_pdf
                              │                                ▼
                         Browser editor              output/YYYY-MM-DD_resume.pdf
                              │
               ┌──────────────┴──────────────┐
               ▼                             ▼
      POST /api/content              POST /api/export
      patch Resume model             export_pdf → download
      resume_to_feed → feed.md
```
