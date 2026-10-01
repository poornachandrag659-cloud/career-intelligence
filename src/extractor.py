"""Rule-based skill extraction + job-description requirement analysis."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache

from .skills_db import CASE_SENSITIVE, SKILL_CATEGORY, SKILLS

PREFERRED_CUES = re.compile(
    r"\b(preferred|nice[- ]to[- ]have|bonus|a plus|is a plus|plus\b|desirable|"
    r"good to have|optional|advantage|ideally|familiarity with)\b", re.I)
REQUIRED_HEADINGS = re.compile(
    r"^\W*(requirements?|qualifications?|must[- ]have|what you(?:'|’)ll need|"
    r"required skills?|what we(?:'|’)re looking for|minimum qualifications?)\b", re.I)
PREFERRED_HEADINGS = re.compile(
    r"^\W*(preferred|nice[- ]to[- ]have|bonus|good to have|desirable|"
    r"preferred qualifications?|extra credit|plus)\b", re.I)
OTHER_HEADINGS = re.compile(
    r"^\W*(responsibilities|about (us|the (role|team|company))|what you(?:'|’)ll do|"
    r"benefits|perks|how to apply|overview|role|why join)\b", re.I)


@lru_cache(maxsize=1)
def _compiled_patterns():
    """[(skill, compiled_regex)] - one regex per skill."""
    out = []
    for category, skills in SKILLS.items():
        for skill, aliases in skills.items():
            ci, cs = [], []
            for a in aliases:
                if skill in CASE_SENSITIVE and a[:1].isupper():
                    cs.append(re.escape(a))
                else:
                    ci.append(re.escape(a))
            regexes = []
            guard = r"(?<![\w+#.])(?:{})(?![\w+#]|\.\w)"
            if ci:
                regexes.append(re.compile(guard.format("|".join(sorted(ci, key=len, reverse=True))), re.I))
            if cs:
                regexes.append(re.compile(guard.format("|".join(sorted(cs, key=len, reverse=True)))))
            out.append((skill, regexes))
    return out


def find_skills(text: str) -> dict[str, int]:
    """Return {canonical_skill: mention_count}."""
    found = {}
    for skill, regexes in _compiled_patterns():
        n = sum(len(r.findall(text)) for r in regexes)
        if n:
            found[skill] = n
    return found


@dataclass
class JobRequirements:
    required: dict[str, int] = field(default_factory=dict)
    preferred: dict[str, int] = field(default_factory=dict)
    years_required: float | None = None

    @property
    def all_skills(self):
        return {**self.preferred, **self.required}


def analyse_job_description(jd: str) -> JobRequirements:
    """Classify each JD skill as required or preferred.

    Rules (transparent & deterministic):
      * lines under a 'Preferred / Nice to have' heading -> preferred
      * lines containing cues like 'is a plus', 'bonus', 'nice to have' -> preferred
      * everything else -> required
      * a skill mentioned in both contexts counts as required
    """
    req: dict[str, int] = {}
    pref: dict[str, int] = {}
    mode = "required"
    for raw in jd.splitlines():
        line = raw.strip()
        if not line:
            continue
        is_heading = len(line) < 60 and (line.endswith(":") or line.isupper() or len(line.split()) <= 5)
        if is_heading:
            if PREFERRED_HEADINGS.match(line):
                mode = "preferred"
            elif REQUIRED_HEADINGS.match(line) or OTHER_HEADINGS.match(line):
                mode = "required"
        line_mode = "preferred" if (mode == "preferred" or PREFERRED_CUES.search(line)) else "required"
        for skill, n in find_skills(line).items():
            target = pref if line_mode == "preferred" else req
            target[skill] = target.get(skill, 0) + n
    for s in list(pref):
        if s in req:
            req[s] += pref.pop(s)
    return JobRequirements(required=req, preferred=pref, years_required=extract_required_years(jd))


def extract_required_years(jd: str) -> float | None:
    """Largest 'N+ years' figure in the JD (a proxy for seniority)."""
    vals = []
    for m in re.finditer(r"(\d{1,2})(?:\s*[-–to]+\s*(\d{1,2}))?\s*\+?\s*(?:years?|yrs?)", jd, re.I):
        lo = int(m.group(1))
        if lo <= 25:
            vals.append(lo)
    return float(min(vals)) if vals else None


_MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec"
_DATE = rf"(?:(?:{_MONTHS})[a-z]*\.?\s+)?((?:19|20)\d{{2}})"
_RANGE = re.compile(rf"{_DATE}\s*(?:-|–|—|to)\s*(?:{_DATE}|(present|current|now|ongoing))", re.I)


_EDU_LINE = re.compile(r"\b(b\.?tech|b\.?e\.?|b\.?sc|m\.?sc|m\.?tech|mba|bachelor|master|ph\.?d|diploma|"
                       r"degree|university|college|school|gpa|cgpa|graduat\w*)\b", re.I)
_EDU_HEADING = re.compile(r"^\W*(education|academics?|certifications?|courses?|projects?)\b", re.I)
_ANY_HEADING = re.compile(r"^\W*(experience|work experience|professional experience|employment|skills|"
                          r"summary|profile|objective|achievements|awards|languages|interests)\b", re.I)


def estimate_resume_years(resume: str, current_year: int | None = None) -> float | None:
    """Estimate years of experience as the union of work date-ranges.

    Date ranges inside Education / Certifications sections, or on lines that
    mention a degree or university, are ignored.
    """
    import datetime
    now = current_year or datetime.date.today().year
    spans, skip = [], False
    for line in resume.splitlines():
        s = line.strip()
        if 0 < len(s) < 45:
            if _EDU_HEADING.match(s):
                skip = True
            elif _ANY_HEADING.match(s):
                skip = False
        if skip or _EDU_LINE.search(s):
            continue
        for m in _RANGE.finditer(s):
            start = int(m.group(1))
            end = now if m.group(3) else int(m.group(2))
            if 1970 <= start <= end <= now + 1:
                spans.append((start, end))
    if not spans:
        explicit = [int(x) for x in re.findall(r"(\d{1,2})\+?\s*years?\s+(?:of\s+)?experience", resume, re.I)]
        return float(max(explicit)) if explicit else None
    spans.sort()
    total, cur_s, cur_e = 0, spans[0][0], spans[0][1]
    for a, b in spans[1:]:
        if a <= cur_e:
            cur_e = max(cur_e, b)
        else:
            total += cur_e - cur_s
            cur_s, cur_e = a, b
    total += cur_e - cur_s
    return float(total)


def categorise(skills) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for s in skills:
        out.setdefault(SKILL_CATEGORY.get(s, "Other"), []).append(s)
    return {k: sorted(v) for k, v in out.items()}
