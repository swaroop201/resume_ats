import json, os
from typing import Dict, List, Tuple
from app.utils.text import tokens

DEFAULT_PATHS = [
    os.path.join("app","resources","roles_profile.json"),
    "roles_profile.json"
]

def _load_roles() -> Dict[str, Dict[str,int]]:
    for p in DEFAULT_PATHS:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}

def extract_resume_skills(text: str) -> List[str]:
    toks = tokens(text)
    return list({t for t in toks if len(t) >= 3})

def rolefit(text: str, top_k: int = 5) -> List[Tuple[str, float, List[str]]]:
    roles = _load_roles()
    if not roles: return []
    res_skills = set(extract_resume_skills(text))
    scored = []
    for role, weights in roles.items():
        score = 0.0
        missing = []
        for skill, w in weights.items():
            if skill in res_skills:
                score += w
            else:
                missing.append(skill)
        scored.append((role, float(score), missing))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
