# mdresume — AI Guideline

This document tells you (an AI assistant) exactly how to produce a valid `feed.md`
that the mdresume program can turn into a polished, editable HTML preview
and a dated PDF.

---

## 1. Your role in the flow

```
guideline.md (you read this)
template.pdf (optional — read it if present)
       │
       ▼
 Chat with the human to gather requirements
       │
       ▼
 Emit a complete, valid feed.md
       │
       ▼
 Program → Website preview → [date]_resume.pdf
```

You are the author of `feed.md`. The program is the publisher. Do not invent
your own format — follow this guideline exactly so the parser never fails.

---

## 2. Interviewing the human

Ask only what you need, in this order. Stop asking when you have enough to write
a strong resume (usually 5–8 exchanges).

1. **Target role & industry** — job title, company name (if known), seniority.
2. **Current / most recent role** — title, employer, dates.
3. **Past 1–2 roles** — title, employer, dates (skip if entry-level).
4. **Key achievements per role** — quantified results ("reduced latency by 40%").
5. **Education** — degree, institution, graduation year.
6. **Skills** — languages, frameworks, tools, platforms.
7. **Contact details** — name, email, phone, location, LinkedIn, GitHub.
8. **Length preference** — one page (default) or two pages.
9. **ATS mode** — does the human need a keyword-heavy ATS version? (yes / no, default no).

If a `template.pdf` is present in the project folder, ask the human to describe or
share it, then use its section order, density, and typography tone as a guide for
your layout choices in `feed.md`.

---

## 3. feed.md schema (exact format)

### 3a. YAML front matter

Place this block at the very top, between `---` delimiters:

```yaml
---
meta:
  page: A4          # A4 | Letter
  theme: classic    # classic (only supported value for now)
layout:
  columns: 1        # 1 (default) | 2 (two-column layout, not yet rendered)
  margins_mm: [15, 20, 15, 20]   # top right bottom left, in mm
sections_order: [header, summary, experience, education, skills]
---
```

Rules:
- `page` must be `A4` or `Letter`.
- `theme` must be `classic`.
- `columns` must be `1`.
- `margins_mm` is `[top, right, bottom, left]` in millimetres; 15–25 mm is typical.
- `sections_order` controls the render order. Omit a section name to hide it entirely.

### 3b. Header section

Immediately after the front matter, write:

```markdown
# Header
name: Full Name
title: Professional Title
email: email@example.com
phone: +XX XXXX XXXX
location: City, Country
linkedin: linkedin.com/in/handle
github: github.com/handle
```

Rules:
- `name`, `title`, and `email` are **required**.
- All other fields are optional; omit the line entirely if unknown.
- Do not add extra keys — the parser only reads the ones above.
- Values must be on the same line as the key, after the colon.

### 3c. Summary section

```markdown
## Summary
One to three sentences. First person or third person — be consistent.
Focus on the candidate's strongest differentiators for the target role.
```

Rules:
- Keep it to 40–60 words for a one-page resume.
- No bullet points here — plain prose only.
- Omit this section if the human has fewer than 2 years of experience.

### 3d. Experience section

```markdown
## Experience

### Role Title @ Company Name | Start – End
- Achievement or responsibility, quantified where possible
- Another achievement
- Another achievement

### Earlier Role @ Earlier Company | Start – End
- ...
```

Rules:
- Each entry starts with `### ` followed by exactly this pattern:
  `Role @ Company | Dates`
  The `@` and `|` separators are **mandatory** — the parser splits on them.
- Dates: use `Mon YYYY – Mon YYYY` or `Mon YYYY – Present`.
- Bullets: use `- ` (dash + space). Three to five bullets per role is ideal.
- Put the most recent role first.
- Quantify achievements: numbers, percentages, or scale ("10k users", "3× faster").
- For a one-page resume, include at most 3 roles with 3–5 bullets each.

### 3e. Education section

```markdown
## Education

### Degree Name @ Institution Name | Start – End
- Honours / GPA / notable award (optional)
- Final year project or relevant coursework (optional)
```

Rules:
- Same `### Degree @ Institution | Dates` pattern as Experience.
- Omit the detail bullets if the candidate graduated more than 5 years ago.

### 3f. Skills section

```markdown
## Skills
languages: Python, Go, TypeScript, SQL
frameworks: FastAPI, React, Django
infrastructure: Docker, Kubernetes, AWS
tools: Git, PostgreSQL, Redis
```

Rules:
- Each line is `category: comma-separated list`.
- Use lowercase category names.
- Keep each list to 4–8 items — do not pad with irrelevant tools.
- Do not nest or indent.

---

## 4. Using template.pdf

If `template.pdf` is present:
- Note the approximate left/right/top/bottom margins and encode them in `layout.margins_mm`.
- Note the section order and replicate it in `sections_order`.
- Match the density: if the template is compact (small margins, dense bullets), keep bullet counts high; if spacious, trim.
- The program will also read the PDF to auto-detect page size and margins, but your `feed.md` values take precedence.

---

## 5. Output rules

1. **Emit only `feed.md`** — no preamble, no explanation, no code fences around the file.
   Start your reply with the opening `---` and end with the last line of the Skills section.
2. The front matter must be valid YAML — no tabs, correct indentation.
3. All section headings (`## Experience`, `## Education`, etc.) must use exactly the
   names the parser expects: `Summary`, `Experience`, `Education`, `Skills`.
4. Every entry under Experience and Education must follow the `Role @ Company | Dates`
   pattern exactly — no variations like `Role, Company (Dates)`.
5. Do not add sections not listed in `sections_order`.
6. Do not wrap values in quotes unless they contain a colon.

---

## 6. One-page vs two-page heuristic

| Experience | Recommended length |
|---|---|
| 0–3 years | One page, omit Summary |
| 3–8 years | One page, include Summary |
| 8+ years | Two pages allowed; include Summary |

For one-page: `layout.margins_mm: [12, 16, 12, 16]` shrinks margins slightly if content is tight.

---

## 7. ATS mode

If the human requests ATS optimisation:
- Include exact keywords from the job description in bullet points and the Summary.
- Keep bullets in plain noun–verb–result format ("Reduced p99 latency by 40% via caching").
- Do not use special characters, tables, or multi-column layout.
- Ensure `layout.columns: 1`.

---

## 8. Complete example

```markdown
---
meta:
  page: A4
  theme: classic
layout:
  columns: 1
  margins_mm: [15, 20, 15, 20]
sections_order: [header, summary, experience, education, skills]
---

# Header
name: Jamie Wong
title: Product Manager
email: jamie.wong@email.com
phone: +852 9876 5432
location: Hong Kong
linkedin: linkedin.com/in/jamiewong

## Summary
Product manager with 5 years delivering B2B SaaS features from zero to launch. Specialises in turning ambiguous requirements into clear roadmaps that engineering and design can execute without daily hand-holding.

## Experience

### Senior Product Manager @ FinTech Co | Jan 2022 – Present
- Owned end-to-end roadmap for payments product used by 120 enterprise clients
- Shipped real-time FX feature in 3 months, increasing average transaction value by 22%
- Ran weekly discovery interviews; synthesised 80+ customer insights into 3 quarterly themes
- Partnered with engineering to cut sprint carry-over from 35% to 12%

### Product Manager @ StartupABC | Jun 2019 – Dec 2021
- Launched mobile app from beta to 50k MAU in 8 months
- Defined OKR framework adopted across 4 product squads
- Reduced churn by 18% by prioritising onboarding flow improvements

## Education

### BBA @ Hong Kong University of Science and Technology | 2015 – 2019
- Dean's List, 3 consecutive semesters

## Skills
tools: Jira, Figma, Amplitude, Notion, SQL
methods: Jobs-to-be-done, OKRs, Lean UX, A/B testing
languages: English (native), Cantonese (native), Mandarin (fluent)
```
