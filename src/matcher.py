"""Transparent match scoring.

Final score = weighted average of independent components. Each component is
0-100 and fully explained in the UI. Components that cannot be computed
(e.g. no 'years of experience' in the JD) are dropped and the remaining weights
are re-normalised, so the score never silently penalises missing data.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .extractor import (JobRequirements, analyse_job_description,
                        estimate_resume_years, find_skills)

DEFAULT_WEIGHTS = {"required": 0.45, "preferred": 0.10, "semantic": 0.30, "experience": 0.15}
# Cosine similarity between a resume and a JD is naturally low (~0.10-0.30 for a
# strong match), so we rescale: cosine >= COSINE_CEILING counts as 100%.
COSINE_CEILING = 0.30


@dataclass
class Component:
    key: str
    label: str
    score: float | None          # 0-100, None if not applicable
    weight: float                # user-set weight
    effective_weight: float = 0  # after re-normalisation
    explanation: str = ""

    @property
    def contribution(self):
        return 0.0 if self.score is None else self.score * self.effective_weight


@dataclass
class MatchResult:
    overall: float
    components: list[Component]
    matched_required: list[str]
    missing_required: list[str]
    matched_preferred: list[str]
    missing_preferred: list[str]
    extra_skills: list[str]
    resume_skills: dict[str, int]
    jd: JobRequirements
    cosine: float
    top_shared_terms: list[tuple[str, float]] = field(default_factory=list)
    top_missing_terms: list[tuple[str, float]] = field(default_factory=list)
    resume_years: float | None = None

    @property
    def verdict(self) -> str:
        s = self.overall
        if s >= 80: return "Excellent fit - apply with confidence"
        if s >= 65: return "Strong fit - minor gaps to close"
        if s >= 45: return "Moderate fit - tailor your resume and upskill"
        return "Stretch role - significant gaps to address"


def tfidf_similarity(resume: str, jd: str):
    """Cosine similarity of TF-IDF vectors + the terms driving it."""
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True,
                          token_pattern=r"(?u)\b[A-Za-z][A-Za-z+#.\-]{1,}\b", min_df=1)
    try:
        X = vec.fit_transform([resume, jd])
    except ValueError:  # empty vocabulary
        return 0.0, [], []
    cos = float(cosine_similarity(X[0], X[1])[0, 0])
    terms = vec.get_feature_names_out()
    r, j = X[0].toarray()[0], X[1].toarray()[0]
    shared = sorted(((terms[i], float(min(r[i], j[i]))) for i in range(len(terms)) if r[i] > 0 and j[i] > 0),
                    key=lambda t: -t[1])[:15]
    missing = sorted(((terms[i], float(j[i])) for i in range(len(terms)) if r[i] == 0 and j[i] > 0),
                     key=lambda t: -t[1])[:15]
    return cos, shared, missing


def _weighted_coverage(wanted: dict[str, int], have: dict[str, int]):
    """Skill coverage where skills mentioned more often in the JD weigh more."""
    if not wanted:
        return None, [], []
    w = {s: 1 + math.log(n) for s, n in wanted.items()}   # 1 mention=1.0, 3 ~ 2.1, 10 ~ 3.3
    total = sum(w.values())
    got = sum(v for s, v in w.items() if s in have)
    matched = sorted([s for s in wanted if s in have], key=lambda s: -w[s])
    missing = sorted([s for s in wanted if s not in have], key=lambda s: -w[s])
    return 100.0 * got / total, matched, missing


def compute_match(resume: str, jd: str, weights: dict[str, float] | None = None) -> MatchResult:
    weights = {**DEFAULT_WEIGHTS, **(weights or {})}
    resume_skills = find_skills(resume)
    jdr = analyse_job_description(jd)

    req_score, m_req, x_req = _weighted_coverage(jdr.required, resume_skills)
    pref_score, m_pref, x_pref = _weighted_coverage(jdr.preferred, resume_skills)
    cos, shared, missing_terms = tfidf_similarity(resume, jd)
    sem_score = min(1.0, cos / COSINE_CEILING) * 100

    ryears = estimate_resume_years(resume)
    exp_score = None
    exp_expl = "Not scored: no 'years of experience' requirement found in the JD."
    if jdr.years_required:
        if ryears is None:
            exp_expl = (f"Not scored: JD asks for {jdr.years_required:g}+ years but no dates "
                        "could be detected on the resume.")
        else:
            exp_score = min(1.0, ryears / jdr.years_required) * 100
            exp_expl = f"Resume shows ~{ryears:g} years vs {jdr.years_required:g}+ requested."

    comps = [
        Component("required", "Required skills", req_score, weights["required"],
                  explanation=(f"{len(m_req)} of {len(jdr.required)} required skills found; "
                               "skills repeated in the JD count more." if jdr.required
                               else "Not scored: no recognised skills in the JD.")),
        Component("preferred", "Preferred skills", pref_score, weights["preferred"],
                  explanation=(f"{len(m_pref)} of {len(jdr.preferred)} nice-to-have skills found."
                               if jdr.preferred else "Not scored: JD lists no nice-to-have skills.")),
        Component("semantic", "Text similarity (TF-IDF)", sem_score, weights["semantic"],
                  explanation=f"Cosine similarity {cos:.2f}; rescaled so {COSINE_CEILING:.2f} = 100%."),
        Component("experience", "Experience level", exp_score, weights["experience"], explanation=exp_expl),
    ]
    active = [c for c in comps if c.score is not None and c.weight > 0]
    tw = sum(c.weight for c in active)
    for c in comps:
        c.effective_weight = (c.weight / tw) if (c in active and tw) else 0.0
    overall = sum(c.contribution for c in comps)

    extra = sorted(s for s in resume_skills if s not in jdr.all_skills)
    return MatchResult(
        overall=round(overall, 1), components=comps,
        matched_required=m_req, missing_required=x_req,
        matched_preferred=m_pref, missing_preferred=x_pref,
        extra_skills=extra, resume_skills=resume_skills, jd=jdr, cosine=cos,
        top_shared_terms=shared, top_missing_terms=missing_terms, resume_years=ryears,
    )
