import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from src.extractor import analyse_job_description, estimate_resume_years, find_skills
from src.matcher import compute_match
from src.parser import DocumentError, read_document
from src.roadmap import build_roadmap

DATA = pathlib.Path(__file__).resolve().parents[1] / "sample_data"
RESUME = (DATA / "sample_resume.txt").read_text()
JD = (DATA / "sample_job_description.txt").read_text()


def test_skill_boundaries():
    s = find_skills("I know JavaScript, Node.js, PostgreSQL, NoSQL, C++ and C#. Not Java.")
    assert "JavaScript" in s and "Node.js" in s and "PostgreSQL" in s
    assert "C++" in s and "C#" in s
    assert "SQL" not in s          # must not match inside PostgreSQL / NoSQL
    assert s.get("Java", 0) == 1   # 'Java' only matched once, not inside JavaScript


def test_nodejs_does_not_imply_javascript():
    assert "JavaScript" not in find_skills("Built services with Node.js")


def test_case_sensitive_ambiguous_words():
    assert "Excel" not in find_skills("We want people who excel at teamwork")
    assert "Excel" in find_skills("Advanced Excel skills")
    assert "React" not in find_skills("we react quickly to incidents")
    assert "React" in find_skills("Built UIs in React")


def test_required_vs_preferred():
    jd = analyse_job_description(JD)
    assert "PyTorch" in jd.required and "Docker" in jd.required
    assert "Terraform" in jd.preferred and "LLMs" in jd.preferred
    assert "Terraform" not in jd.required
    assert jd.years_required == 3.0


def test_years_estimation_union():
    r = "Dev 2015 - 2018\nLead 2017 - 2020\nOther Jan 2022 - Present"
    assert estimate_resume_years(r, current_year=2025) == 8.0   # 2015-2020 (5) + 2022-2025 (3)


def test_education_dates_ignored():
    r = "EXPERIENCE\nDev  Jun 2020 - Present\nEDUCATION\nB.Tech 2014 - 2018"
    assert estimate_resume_years(r, current_year=2025) == 5.0


def test_match_score_range_and_weights():
    res = compute_match(RESUME, JD)
    assert 0 <= res.overall <= 100
    assert abs(sum(c.effective_weight for c in res.components if c.score is not None) - 1) < 1e-9
    assert "Python" in res.matched_required and "PyTorch" in res.missing_required


def test_identical_docs_score_high_and_unrelated_low():
    assert compute_match(JD, JD).overall > 85
    assert compute_match("I bake sourdough bread and paint landscapes.", JD).overall < 20


def test_missing_experience_component_renormalises():
    res = compute_match(RESUME, "Python and SQL developer needed. Nice to have: Docker.")
    exp = [c for c in res.components if c.key == "experience"][0]
    assert exp.score is None and exp.effective_weight == 0


def test_roadmap_orders_prereqs_first():
    res = compute_match("Python developer. SQL.", JD)
    rm = build_roadmap(res)
    names = [i.skill for i in rm.items]
    assert names.index("Machine Learning") < names.index("Deep Learning") < names.index("PyTorch") \
        if "PyTorch" in names else True
    assert rm.total_hours > 0 and rm.weeks >= 1
    assert all(i.resources for i in rm.items)


def test_pdf_roundtrip():
    data = (DATA / "sample_resume.pdf").read_bytes()
    text = read_document("sample_resume.pdf", data)
    assert "PostgreSQL" in text


def test_empty_pdf_error():
    try:
        read_document("x.txt", b"   ")
    except DocumentError:
        return
    raise AssertionError("expected DocumentError")
