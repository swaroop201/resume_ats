import re
from typing import List, Tuple
from app.utils.text import detect_sections

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

def ats_assess(text: str, filename: str) -> Tuple[int, List[str]]:
    tips: List[str] = []

    words = len(text.split())
    if words < 150:
        tips.append("Resume seems very short; add more detail (~1 page).")
    elif words > 1600:
        tips.append("Resume is quite long; consider trimming to 1–2 pages.")

    sec = detect_sections(text)
    if sec["count"] < 2:
        tips.append("Add standard sections (Experience, Education, Skills).")

    if not EMAIL_RE.search(text):
        tips.append("Add a professional email address.")

    ext = filename.lower().split(".")[-1]
    if ext not in {"pdf", "docx", "txt"}:
        tips.append("Use PDF or DOCX for ATS friendliness.")

    score = 100
    score -= 15 if words < 150 or words > 1800 else 0
    score -= 20 if sec["count"] < 2 else 0
    score -= 10 if not EMAIL_RE.search(text) else 0
    score = max(0, min(100, score))

    return score, tips
