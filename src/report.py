"""Markdown / JSON export of an analysis."""
from __future__ import annotations

import json

from .matcher import MatchResult
from .roadmap import Roadmap, roadmap_markdown


def result_to_dict(r: MatchResult) -> dict:
    return {
        "overall_score": r.overall,
        "verdict": r.verdict,
        "components": [
            {"component": c.label, "score": None if c.score is None else round(c.score, 1),
             "user_weight": c.weight, "effective_weight": round(c.effective_weight, 3),
             "contribution": round(c.contribution, 2), "explanation": c.explanation}
            for c in r.components
        ],
        "matched_required": r.matched_required, "missing_required": r.missing_required,
        "matched_preferred": r.matched_preferred, "missing_preferred": r.missing_preferred,
        "extra_skills": r.extra_skills, "cosine_similarity": round(r.cosine, 4),
        "estimated_resume_years": r.resume_years,
    }


def build_markdown_report(r: MatchResult, rm: Roadmap | None = None) -> str:
    L = [f"# Career Match Report", "", f"## Overall match: {r.overall:.0f}/100", f"**{r.verdict}**", "",
         "## Score breakdown", "", "| Component | Score | Weight used | Contribution |", "|---|---|---|---|"]
    for c in r.components:
        sc = "n/a" if c.score is None else f"{c.score:.0f}"
        L.append(f"| {c.label} | {sc} | {c.effective_weight:.0%} | {c.contribution:.1f} |")
    L += ["", "## Skills", "",
          f"- **Matched required:** {', '.join(r.matched_required) or 'none'}",
          f"- **Missing required:** {', '.join(r.missing_required) or 'none'}",
          f"- **Matched preferred:** {', '.join(r.matched_preferred) or 'none'}",
          f"- **Missing preferred:** {', '.join(r.missing_preferred) or 'none'}",
          f"- **Extra skills you bring:** {', '.join(r.extra_skills) or 'none'}", ""]
    if rm and rm.items:
        L.append(roadmap_markdown(rm))
    return "\n".join(L)


def to_json(r: MatchResult, rm: Roadmap | None = None) -> str:
    d = result_to_dict(r)
    if rm:
        d["roadmap"] = [{"phase": i.phase, "skill": i.skill, "priority": i.priority, "hours": i.hours,
                         "reason": i.reason, "resources": [{"title": t, "url": u} for t, u in i.resources]}
                        for i in rm.items]
    return json.dumps(d, indent=2)
