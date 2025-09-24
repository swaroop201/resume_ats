from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.parsing import extract_text_from_bytes
from app.services.diagnostics import sec_diagnose
from app.services.roles import rolefit
from app.services.resources import recommend_for_gaps

router = APIRouter(prefix="/diagnose", tags=["diagnose"])

@router.post("/sec")
async def skill_evidence_check(file: UploadFile = File(...)):
    data = await file.read()
    text, _ = extract_text_from_bytes(data, file.filename)
    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text")
    return sec_diagnose(text)

@router.post("/rolefit")
async def role_fit(file: UploadFile = File(...)):
    data = await file.read()
    text, _ = extract_text_from_bytes(data, file.filename)
    ranked = rolefit(text, top_k=5)
    return {
        "top_roles": [
            {"role": r, "score": s, "top_missing_skills": missing[:5]}
            for (r, s, missing) in ranked
        ]
    }

@router.post("/actions")
async def actions_for_gaps(file: UploadFile = File(...), max_items: int = 3):
    data = await file.read()
    text, _ = extract_text_from_bytes(data, file.filename)
    sec = sec_diagnose(text)
    gaps = (sec.get("weak") or []) + (sec.get("unsupported") or [])
    recs = recommend_for_gaps(gaps, max_items=max_items)
    return {"gaps": gaps, "recommendations": recs}
