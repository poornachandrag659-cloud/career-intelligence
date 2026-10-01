"""Turn skill gaps into an ordered, time-boxed learning roadmap."""
from __future__ import annotations

import math
from dataclasses import dataclass

from .matcher import MatchResult
from .skills_db import PREREQUISITES, SKILL_CATEGORY, hours_for, resources_for


@dataclass
class RoadmapItem:
    skill: str
    category: str
    priority: str            # "Critical" | "Important" | "Nice to have" | "Prerequisite"
    hours: int
    reason: str
    resources: list[tuple[str, str]]
    phase: int = 1


@dataclass
class Roadmap:
    items: list[RoadmapItem]
    weeks: int
    hours_per_week: int

    @property
    def total_hours(self):
        return sum(i.hours for i in self.items)

    def by_phase(self):
        phases: dict[int, list[RoadmapItem]] = {}
        for i in self.items:
            phases.setdefault(i.phase, []).append(i)
        return dict(sorted(phases.items()))


def build_roadmap(result: MatchResult, hours_per_week: int = 8, max_skills: int = 12,
                  include_preferred: bool = True) -> Roadmap:
    resume_has = set(result.resume_skills)
    targets: list[tuple[str, str, str]] = []   # (skill, priority, reason)
    for s in result.missing_required:
        n = result.jd.required.get(s, 1)
        pr = "Critical" if n >= 2 else "Important"
        targets.append((s, pr, f"Required by the JD (mentioned {n}x)."))
    if include_preferred:
        for s in result.missing_preferred:
            targets.append((s, "Nice to have", "Listed as preferred / a plus in the JD."))
    targets = targets[:max_skills]

    chosen = {s: (p, r) for s, p, r in targets}
    # pull in missing prerequisites (recursively) the candidate lacks
    def add_prereqs(skill, depth=0):
        for pre in PREREQUISITES.get(skill, []):
            if pre in resume_has or depth > 5:
                continue
            if pre not in chosen:
                chosen[pre] = ("Prerequisite", f"Foundation needed before {skill}.")
            add_prereqs(pre, depth + 1)
    for s in list(chosen):
        add_prereqs(s)

    # topological order: prerequisites first, then by priority
    order_rank = {"Prerequisite": 0, "Critical": 1, "Important": 2, "Nice to have": 3}
    ordered, seen = [], set()

    def visit(skill):
        if skill in seen:
            return
        seen.add(skill)
        for pre in PREREQUISITES.get(skill, []):
            if pre in chosen:
                visit(pre)
        ordered.append(skill)

    pos = {s: i for i, (s, _, _) in enumerate(targets)}   # JD-importance order
    for s in sorted(chosen, key=lambda k: (order_rank[chosen[k][0]], pos.get(k, 0), k)):
        visit(s)

    items = [RoadmapItem(s, SKILL_CATEGORY.get(s, "Other"), chosen[s][0], hours_for(s),
                         chosen[s][1], resources_for(s)) for s in ordered]

    # assign phases by cumulative hours (~ 4 weeks each)
    total_h = sum(i.hours for i in items)
    phase_hours = max(hours_per_week * 4, math.ceil(total_h / 4))   # at most ~4-5 phases
    acc, phase = 0, 1
    for it in items:
        if acc and acc + it.hours > phase_hours:
            phase += 1
            acc = 0
        it.phase = phase
        acc += it.hours
    total = sum(i.hours for i in items)
    return Roadmap(items=items, weeks=max(1, math.ceil(total / max(1, hours_per_week))),
                   hours_per_week=hours_per_week)


def roadmap_markdown(rm: Roadmap, title: str = "Personalised Learning Roadmap") -> str:
    lines = [f"# {title}", "",
             f"**Estimated effort:** {rm.total_hours} hours (~{rm.weeks} weeks at {rm.hours_per_week} h/week)", ""]
    for ph, items in rm.by_phase().items():
        lines += [f"## Phase {ph}", ""]
        for i in items:
            lines.append(f"### {i.skill}  ({i.priority}, ~{i.hours} h)")
            lines.append(f"_{i.reason}_")
            for t, u in i.resources:
                lines.append(f"- [{t}]({u})")
            lines.append("")
    return "\n".join(lines)
