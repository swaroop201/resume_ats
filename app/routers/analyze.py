from fastapi import APIRouter, UploadFile, File, Form
from app.config import config
from app.schemas import AnalyzeOneResponse, ResumeResult, ATSReport, Explanation
from app.services import parsing, scoring as scoring_svc, explain as explain_svc, ats_check

router = APIRouter(prefix="/analyze", tags=["analyze"])

@router.post("/", response_model=AnalyzeOneResponse)
async def analyze_one(
    job_description: str = Form(...),
    file: UploadFile = File(...),
    use_embeddings: bool = Form(None),
    blend_weight: float = Form(None),
    top_k_terms: int = Form(None)
):
    # Read inputs
    jd_text = job_description.strip()
    data = await file.read()
    resume_text, _ = parsing.extract_text_from_bytes(data, file.filename)

    # Resolve config
    use_emb = config.use_embeddings if use_embeddings is None else bool(use_embeddings)
    blend = config.blend_weight if blend_weight is None else float(blend_weight)
    topk = config.top_k_terms if top_k_terms is None else int(top_k_terms)

    # Score (TF-IDF + optional embeddings)
    engine = scoring_svc.ResumeScorer(use_embeddings=use_emb)
    res = engine.score(jd_text, [resume_text])  # single resume in a list
    blended = scoring_svc.ResumeScorer.blend(res.tfidf_scores, res.embed_scores, blend)

    # Explain + ATS
    matched_skills, missing_skills, matched_terms, missing_terms = explain_svc.explain_matches(
        jd_text, resume_text, top_k_terms=topk
    )
    ats_score, tips = ats_check.ats_assess(resume_text, file.filename)

    # Build single result
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

    return AnalyzeOneResponse(
        job_description_preview=jd_text[:500],
        engine="tfidf+embeddings" if use_emb and res.embed_scores is not None else "tfidf",
        result=result,
    )
