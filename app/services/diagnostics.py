from collections import defaultdict
import re
from typing import Dict, List, Set
from app.utils.text import normalize_text

ACTION_VERBS = {
    "built","developed","implemented","designed","automated","deployed","optimized",
    "migrated","integrated","analyzed","modeled","visualized","orchestrated","maintained",
    "tested","benchmarked","refactored","shipped","owned","scaled"
}
OBJECT_HINTS = {
    "api","service","pipeline","etl","dashboard","model","classifier","regression",
    "notebook","dataset","feature","training","deployment","container","cluster","workflow"
}

SEC_WEAK = 0.10
SEC_STRONG = 0.40

def _sentences(text: str) -> List[str]:
    return re.split(r"[.\n;]+", text)

def claimed_skills_from_section(resume_text: str) -> Set[str]:
    t = resume_text.lower()
    idx = t.find("skills")
    if idx == -1:
        return set()
    chunk = t[idx: idx + 1200]
    items = re.split(r"[,:|/•\n\t]", chunk)
    skills = set()
    for it in items:
        it = it.strip().lower()
        if 2 <= len(it) <= 32 and re.search(r"[a-z]", it) and "skills" not in it:
            skills.add(it)
    return {s for s in skills if len(s) >= 2}

def evidence_scores(resume_text: str, skills: Set[str]) -> Dict[str, float]:
    sents = [normalize_text(s).lower() for s in _sentences(resume_text)]
    scores = defaultdict(float)
    for s in sents:
        for skill in skills:
            if skill in s:
                has_verb = any(v in s for v in ACTION_VERBS)
                has_obj  = any(o in s for o in OBJECT_HINTS)
                base = 0.15
                if has_verb: base += 0.25
                if has_obj:  base += 0.20
                scores[skill] = max(scores[skill], base)
    return {k: min(1.0, v) for k, v in scores.items()}

def sec_diagnose(resume_text: str) -> Dict[str, List[str]]:
    claimed = claimed_skills_from_section(resume_text)
    if not claimed:
        return {"claimed_skills": [], "supported": [], "weak": [], "unsupported": []}
    scores = evidence_scores(resume_text, claimed)
    supported, weak, unsupported = [], [], []
    for s in claimed:
        v = scores.get(s, 0.0)
        if v >= SEC_STRONG:
            supported.append(s)
        elif v >= SEC_WEAK:
            weak.append(s)
        else:
            unsupported.append(s)
    return {
        "claimed_skills": sorted(claimed),
        "supported": sorted(set(supported)),
        "weak": sorted(set(weak)),
        "unsupported": sorted(set(unsupported)),
    }
