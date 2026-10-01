"""AI Career Intelligence Platform - Streamlit app.

Run:  streamlit run app.py
"""
from pathlib import Path

import pandas as pd
import streamlit as st

from src.extractor import categorise
from src.matcher import DEFAULT_WEIGHTS, compute_match
from src.parser import DocumentError, read_document
from src.report import build_markdown_report, to_json
from src.roadmap import build_roadmap

SAMPLE_DIR = Path(__file__).parent / "sample_data"

st.set_page_config(page_title="AI Career Intelligence Platform", page_icon="🧭", layout="wide")


# ---------------------------------------------------------------- helpers
def load_input(label: str, key: str, sample_file: str, use_sample: bool) -> str:
    """Upload-or-paste widget. Returns text ('' if nothing provided)."""
    st.subheader(label)
    if use_sample:
        text = (SAMPLE_DIR / sample_file).read_text(encoding="utf-8")
        st.text_area("Sample loaded (editable)", text, height=260, key=f"{key}_sample")
        return st.session_state.get(f"{key}_sample", text)
    up = st.file_uploader("Upload PDF, DOCX or TXT", type=["pdf", "docx", "txt"], key=f"{key}_file")
    if up is not None:
        try:
            text = read_document(up.name, up.getvalue())
            with st.expander(f"Preview extracted text ({len(text.split())} words)"):
                st.text(text[:3000] + ("..." if len(text) > 3000 else ""))
            return text
        except DocumentError as e:
            st.error(str(e))
            return ""
    return st.text_area("...or paste text", height=200, key=f"{key}_paste")


def chips(skills, color="green"):
    if not skills:
        st.caption("None")
        return
    st.markdown(" ".join(f":{color}-badge[{s}]" for s in skills))


def score_color(score: float) -> str:
    return "green" if score >= 65 else "orange" if score >= 45 else "red"


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.title("🧭 Career Intelligence")
    st.caption("Resume ↔ Job match, skill gaps, and a learning plan.")
    use_sample = st.toggle("Use sample data", value=False,
                           help="Loads a demo resume + ML Engineer job description.")
    st.divider()
    st.markdown("**Score weights**  \nAdjust what matters; weights are re-normalised automatically.")
    w = {
        "required": st.slider("Required skills", 0, 100, int(DEFAULT_WEIGHTS["required"] * 100), 5),
        "preferred": st.slider("Preferred skills", 0, 100, int(DEFAULT_WEIGHTS["preferred"] * 100), 5),
        "semantic": st.slider("Text similarity (TF-IDF)", 0, 100, int(DEFAULT_WEIGHTS["semantic"] * 100), 5),
        "experience": st.slider("Experience level", 0, 100, int(DEFAULT_WEIGHTS["experience"] * 100), 5),
    }
    st.divider()
    st.markdown("**Learning plan**")
    hpw = st.slider("Hours you can study per week", 2, 40, 8)
    max_skills = st.slider("Max skills in roadmap", 3, 20, 10)
    inc_pref = st.checkbox("Include nice-to-have skills", value=True)

# ---------------------------------------------------------------- main
st.title("AI Career Intelligence Platform")
st.write("Upload a resume and a job description to extract skills, find gaps, get a "
         "**transparent match score**, and receive a personalised learning roadmap.")

c1, c2 = st.columns(2)
with c1:
    resume_text = load_input("1. Your resume", "resume", "sample_resume.txt", use_sample)
with c2:
    jd_text = load_input("2. Job description", "jd", "sample_job_description.txt", use_sample)

go = st.button("Analyse match", type="primary", disabled=not (resume_text.strip() and jd_text.strip()))
if not (resume_text.strip() and jd_text.strip()):
    st.info("Provide both a resume and a job description (or toggle **Use sample data** in the sidebar).")

if go:
    if sum(w.values()) == 0:
        st.error("At least one score weight must be above zero.")
    else:
        with st.spinner("Analysing..."):
            res = compute_match(resume_text, jd_text, {k: v / 100 for k, v in w.items()})
            rm = build_roadmap(res, hours_per_week=hpw, max_skills=max_skills, include_preferred=inc_pref)
        st.session_state["analysis"] = (res, rm)

if "analysis" in st.session_state:
    res, rm = st.session_state["analysis"]
    st.divider()

    top1, top2, top3, top4 = st.columns(4)
    top1.metric("Overall match", f"{res.overall:.0f} / 100")
    top2.metric("Required skills met", f"{len(res.matched_required)}/{len(res.jd.required)}")
    top3.metric("Skill gaps", len(res.missing_required) + len(res.missing_preferred))
    top4.metric("Est. time to close gaps", f"{rm.weeks} wks" if rm.items else "-")
    st.progress(min(1.0, res.overall / 100))
    st.markdown(f":{score_color(res.overall)}[**{res.verdict}**]")

    tab_score, tab_skills, tab_kw, tab_road, tab_export = st.tabs(
        ["📊 Score breakdown", "🧩 Skills & gaps", "🔎 Keywords (TF-IDF)", "🗺️ Learning roadmap", "⬇️ Export"])

    # ---- score breakdown
    with tab_score:
        st.markdown("The overall score is the **weighted average** of the components below. "
                    "Components that can't be computed are dropped and the other weights re-scaled.")
        df = pd.DataFrame([{
            "Component": c.label,
            "Score (0-100)": None if c.score is None else round(c.score, 1),
            "Weight you set": f"{c.weight:.0%}" if c.weight <= 1 else f"{c.weight:.0f}",
            "Weight used": f"{c.effective_weight:.0%}",
            "Contribution (pts)": round(c.contribution, 1),
            "Why": c.explanation,
        } for c in res.components])
        st.dataframe(df, hide_index=True)
        chart_df = pd.DataFrame({"Contribution (pts)": [round(c.contribution, 1) for c in res.components]},
                                index=[c.label for c in res.components])
        st.bar_chart(chart_df)
        st.caption(f"Sum of contributions = {res.overall:.1f}")

    # ---- skills
    with tab_skills:
        a, b = st.columns(2)
        with a:
            st.markdown("#### ✅ Matched required")
            chips(res.matched_required, "green")
            st.markdown("#### ✅ Matched preferred")
            chips(res.matched_preferred, "blue")
        with b:
            st.markdown("#### ❌ Missing required")
            chips(res.missing_required, "red")
            st.markdown("#### ⚠️ Missing preferred")
            chips(res.missing_preferred, "orange")
        st.markdown("#### ➕ Extra skills you bring (not asked for)")
        chips(res.extra_skills, "gray")
        with st.expander("All skills detected on your resume, by category"):
            for cat, skills in categorise(res.resume_skills).items():
                st.markdown(f"**{cat}**")
                chips(skills, "violet")
        with st.expander("How is 'required' vs 'preferred' decided?"):
            st.markdown("- Lines under a *Nice to have / Preferred / Bonus* heading, or containing cues like "
                        "*'a plus'*, are **preferred**.\n- Everything else is **required**.\n"
                        "- Skills repeated more often in the JD carry more weight (1 + ln(mentions)).")

    # ---- keywords
    with tab_kw:
        k1, k2 = st.columns(2)
        with k1:
            st.markdown("#### Terms you share with the JD")
            st.dataframe(pd.DataFrame(res.top_shared_terms, columns=["Term", "TF-IDF weight"]),
                         hide_index=True)
        with k2:
            st.markdown("#### Important JD terms missing from your resume")
            st.dataframe(pd.DataFrame(res.top_missing_terms, columns=["Term", "TF-IDF weight"]),
                         hide_index=True)
        st.caption(f"Cosine similarity between TF-IDF vectors: {res.cosine:.3f}. "
                   "Add genuinely relevant missing terms to your resume (only if they are true!).")

    # ---- roadmap
    with tab_road:
        if not rm.items:
            st.success("No skill gaps found - nothing to learn for this role. 🎉")
        else:
            st.markdown(f"**{rm.total_hours} hours** total ≈ **{rm.weeks} weeks** at {rm.hours_per_week} h/week.")
            for ph, items in rm.by_phase().items():
                ph_hours = sum(i.hours for i in items)
                st.markdown(f"### Phase {ph}  ·  ~{ph_hours} h")
                for it in items:
                    with st.expander(f"{it.skill}  —  {it.priority}  ·  ~{it.hours} h", expanded=(ph == 1)):
                        st.write(it.reason)
                        st.markdown("\n".join(f"- [{t}]({u})" for t, u in it.resources))
                        st.markdown("**Portfolio idea:** build a small project using "
                                    f"**{it.skill}** and add it to your resume/GitHub.")

    # ---- export
    with tab_export:
        md = build_markdown_report(res, rm)
        st.download_button("Download report (Markdown)", md, "career_report.md", "text/markdown")
        st.download_button("Download data (JSON)", to_json(res, rm), "career_analysis.json", "application/json")
        with st.expander("Preview report"):
            st.markdown(md)
