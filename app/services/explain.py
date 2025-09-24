from collections import Counter
from typing import List, Tuple
from app.utils.text import tokens
from app.services.skills import ALL_SKILLS

def extract_terms(text: str, top_k: int = 25) -> List[str]:
    toks = tokens(text)
    freq = Counter(toks)
    ranked = [t for t,_ in freq.most_common() if len(t) >= 3]
    return ranked[:top_k]

def explain_matches(jd_text: str, resume_text: str, top_k_terms: int = 25) -> Tuple[list, list, list, list]:
    jd_terms = set(extract_terms(jd_text, top_k_terms))
    res_terms = set(extract_terms(resume_text, top_k_terms*2))

    matched_terms = sorted(jd_terms & res_terms)
    missing_terms = sorted(jd_terms - res_terms)

    jd_skills = {s for s in ALL_SKILLS if s in jd_text.lower()}
    res_skills = {s for s in ALL_SKILLS if s in resume_text.lower()}

    matched_skills = sorted(jd_skills & res_skills)
    missing_skills = sorted(jd_skills - res_skills)

    return matched_skills, missing_skills, matched_terms, missing_terms
