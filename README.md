# 🧭 AI Career Intelligence Platform

Upload a resume and a job description → extract skills, find gaps, get a **transparent match score**,
and receive a **personalised learning roadmap**. Built with Python, Streamlit, scikit-learn (TF-IDF + cosine
similarity) and pypdf.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Toggle **Use sample data** in the sidebar for an instant demo. Run tests with `pytest -q`.

## Project layout
```
app.py                 Streamlit UI (tabs: score, skills, keywords, roadmap, export)
src/parser.py          PDF / DOCX / TXT -> clean text (clear errors for scanned PDFs)
src/skills_db.py       ~150-skill taxonomy, aliases, prerequisites, hours, learning links
src/extractor.py       Regex skill extraction, required-vs-preferred detection, experience years
src/matcher.py         TF-IDF cosine similarity + weighted, explainable score
src/roadmap.py         Prerequisite-aware, phased learning plan
src/report.py          Markdown / JSON export
tests/test_core.py     Unit tests
sample_data/           Demo resume (txt + pdf) and job description
```

## How the score works (fully transparent)
`Overall = Σ (component score × weight)`, weights are user-adjustable and re-normalised.

| Component | Default weight | How it's computed |
|---|---|---|
| Required skills | 45% | Weighted coverage of JD "required" skills found in resume. Skill weight = 1 + ln(mentions in JD) |
| Preferred skills | 10% | Same, for "nice to have" skills |
| Text similarity | 30% | TF-IDF (1-2 grams, sublinear tf) cosine similarity, rescaled so 0.30 → 100% |
| Experience | 15% | min(1, resume years / JD years). Resume years = union of work date ranges (education ignored) |

If a component can't be computed (e.g. JD states no years), it is dropped and the others re-scaled —
missing data never silently lowers your score.

## Roadmap logic
Missing skills (ranked by JD importance) → pull in missing prerequisites (e.g. PyTorch ← Deep Learning ← Machine
Learning) → topological order → grouped into phases using your weekly study hours → curated official resources
(or search links when none are curated).

## Ideas to extend
- Swap regex extraction for spaCy `PhraseMatcher` or a sentence-embedding model (`sentence-transformers`)
- Add OCR (`pytesseract`) for scanned PDFs
- Add a resume-rewrite suggestions tab using an LLM API
- Persist history with SQLite and chart score progress over time
