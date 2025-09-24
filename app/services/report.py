from io import BytesIO
from typing import List
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem

def _bullets(items: List[str], style) -> ListFlowable:
    if not items:
        items = ["None"]
    return ListFlowable(
        [ListItem(Paragraph(x, style), leftIndent=12) for x in items],
        bulletType="bullet",
        start="disc",
        leftIndent=0
    )

def build_pdf(result, engine: str, jd_preview: str) -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        leftMargin=48, rightMargin=48, topMargin=48, bottomMargin=48
    )

    styles = getSampleStyleSheet()
    h1 = styles["Heading1"]
    h2 = styles["Heading2"]
    body = styles["BodyText"]
    body.leading = 14
    small = ParagraphStyle("small", parent=body, fontSize=9, leading=12, alignment=TA_LEFT, textColor=colors.grey)

    story = []
    # Title
    story.append(Paragraph("Resume Analysis Report", h1))
    story.append(Spacer(1, 8))
    story.append(Paragraph("This report summarizes match score, ATS checks, and key skill/term overlap.", small))
    story.append(Spacer(1, 16))

    # Overview table
    kv = [
        ["Filename", result.filename],
        ["Engine", engine],
        ["Final Score", f"{result.score:.3f}"],
        ["TF-IDF Score", f"{result.tfidf_score:.3f}"],
        ["Embeddings Score", "—" if result.embed_score is None else f"{result.embed_score:.3f}"],
        ["ATS Score", str(result.ats.score)],
    ]
    t = Table(kv, hAlign="LEFT", colWidths=[120, 360])
    t.setStyle(TableStyle([
        ("FONT", (0,0), (-1,-1), "Helvetica", 10),
        ("TEXTCOLOR", (0,0), (0,-1), colors.grey),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # JD Preview
    story.append(Paragraph("Job Description Preview", h2))
    story.append(Paragraph(jd_preview if jd_preview else "—", body))
    story.append(Spacer(1, 10))

    # ATS Tips
    story.append(Paragraph("ATS Tips", h2))
    story.append(_bullets(result.ats.tips, body))
    story.append(Spacer(1, 10))

    # Skills / Terms
    story.append(Paragraph("Matched Skills", h2))
    story.append(_bullets(result.explanation.matched_skills, body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Missing Skills", h2))
    story.append(_bullets(result.explanation.missing_skills, body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Matched Terms", h2))
    story.append(_bullets(result.explanation.matched_terms, body))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Missing Terms", h2))
    story.append(_bullets(result.explanation.missing_terms, body))

    doc.build(story)
    return buf.getvalue()
