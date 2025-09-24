from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import config
from app.services import parsing, scoring as scoring_svc, explain as explain_svc, ats_check
from app.schemas import ResumeResult, ATSReport, Explanation

router = APIRouter(prefix="/ui", tags=["ui"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def ui_form(request: Request):
    return templates.TemplateResponse("ui_form.html", {"request": request})

@router.post("/analyze", response_class=HTMLResponse)
async def ui_analyze(
    request: Request,
    jd_text: str = Form(...),
    file: UploadFile = File(...),
    use_embeddings: str = Form(None)  # "true", "false", or None
):
    jd = jd_text.strip()
    data = await file.read()
    resume_text, _ = parsing.extract_text_from_bytes(data, file.filename)

    if use_embeddings is None or use_embeddings == "":
        use_emb = config.use_embeddings
    else:
        use_emb = True if str(use_embeddings).lower() == "true" else False

    engine = scoring_svc.ResumeScorer(use_embeddings=use_emb)
    res = engine.score(jd, [resume_text])
    blended = scoring_svc.ResumeScorer.blend(res.tfidf_scores, res.embed_scores, config.blend_weight)

    matched_skills, missing_skills, matched_terms, missing_terms = explain_svc.explain_matches(
        jd, resume_text, top_k_terms=config.top_k_terms
    )
    ats_score, tips = ats_check.ats_assess(resume_text, file.filename)

    result = ResumeResult(
        filename=file.filename,
        score=float(blended[0]),
        tfidf_score=float(res.tfidf_scores[0]),
        embed_score=float(res.embed_scores[0]) if res.embed_scores is not None else None,
        ats=ATSReport(score=ats_score, tips=tips),
        explanation=Explanation(
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            matched_terms=matched_terms,
            missing_terms=missing_terms,
        ),
    )

    return templates.TemplateResponse("ui_result.html", {
        "request": request,
        "engine": "tfidf+embeddings" if use_emb and res.embed_scores is not None else "tfidf",
        "result": result
    })
from fastapi.responses import StreamingResponse
from app.services import report as report_svc

@router.post("/report")
async def ui_report(
    jd_text: str = Form(...),
    file: UploadFile = File(...),
    use_embeddings: str = Form(None)
):
    # Recompute result (same as /ui/analyze)
    jd = jd_text.strip()
    data = await file.read()
    resume_text, _ = parsing.extract_text_from_bytes(data, file.filename)

    if use_embeddings is None or use_embeddings == "":
        use_emb = config.use_embeddings
    else:
        use_emb = True if str(use_embeddings).lower() == "true" else False

    engine = scoring_svc.ResumeScorer(use_embeddings=use_emb)
    res = engine.score(jd, [resume_text])
    blended = scoring_svc.ResumeScorer.blend(res.tfidf_scores, res.embed_scores, config.blend_weight)

    matched_skills, missing_skills, matched_terms, missing_terms = explain_svc.explain_matches(
        jd, resume_text, top_k_terms=config.top_k_terms
    )
    ats_score, tips = ats_check.ats_assess(resume_text, file.filename)

    result = ResumeResult(
        filename=file.filename,
        score=float(blended[0]),
        tfidf_score=float(res.tfidf_scores[0]),
        embed_score=float(res.embed_scores[0]) if res.embed_scores is not None else None,
        ats=ATSReport(score=ats_score, tips=tips),
        explanation=Explanation(
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            matched_terms=matched_terms,
            missing_terms=missing_terms,
        ),
    )

    pdf_bytes = report_svc.build_pdf(
        result=result,
        engine="tfidf+embeddings" if use_emb and res.embed_scores is not None else "tfidf",
        jd_preview=jd[:500]
    )

    safe_name = file.filename.replace(" ", "_")
    headers = {"Content-Disposition": f'attachment; filename="analysis_{safe_name}.pdf"'}
    return StreamingResponse(iter([pdf_bytes]), media_type="application/pdf", headers=headers)
