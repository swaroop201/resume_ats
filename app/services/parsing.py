from io import BytesIO
from typing import Tuple
from pathlib import Path
import tempfile

from PyPDF2 import PdfReader
import docx2txt

from app.utils.text import normalize_text

SUPPORTED = {".pdf", ".docx", ".txt"}

def extract_text_from_bytes(data: bytes, filename: str) -> Tuple[str, str]:
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED:
        try:
            text = data.decode("utf-8", errors="ignore")
        except Exception:
            text = ""
        return normalize_text(text), ext or "unknown"

    if ext == ".pdf":
        text = []
        with BytesIO(data) as bio:
            reader = PdfReader(bio)
            for page in reader.pages:
                try:
                    text.append(page.extract_text() or "")
                except Exception:
                    continue
        return normalize_text("\n".join(text)), ext

    if ext == ".docx":
        with tempfile.NamedTemporaryFile(suffix=ext) as tf:
            tf.write(data)
            tf.flush()
            txt = docx2txt.process(tf.name) or ""
            return normalize_text(txt), ext

    if ext == ".txt":
        return normalize_text(data.decode("utf-8", errors="ignore")), ext

    return normalize_text(""), ext
