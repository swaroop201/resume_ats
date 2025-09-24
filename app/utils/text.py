import re
from unidecode import unidecode

_WS_RE = re.compile(r"\s+")
_WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}")

SECTION_TOKENS = [
    "experience", "work experience", "education", "skills", "projects",
    "certifications", "summary", "contact", "publications"
]

def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = unidecode(s)
    s = s.replace("\x00", " ")
    s = _WS_RE.sub(" ", s)
    return s.strip()

def tokens(text: str) -> list:
    return [t.lower() for t in _WORD_RE.findall(text.lower())]

def detect_sections(text: str) -> dict:
    t = text.lower()
    found = [sec for sec in SECTION_TOKENS if sec in t]
    return {"found": found, "count": len(found)}
