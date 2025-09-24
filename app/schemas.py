from typing import List, Optional
from pydantic import BaseModel, Field

class ATSReport(BaseModel):
    score: int
    tips: List[str] = []

class Explanation(BaseModel):
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    matched_terms: List[str] = []
    missing_terms: List[str] = []

class ResumeResult(BaseModel):
    filename: str
    score: float = Field(..., description="Final blended similarity score 0..1")
    tfidf_score: float
    embed_score: Optional[float] = None
    ats: ATSReport
    explanation: Explanation

class AnalyzeOneResponse(BaseModel):
    job_description_preview: str
    engine: str
    result: ResumeResult


class ConfigModel(BaseModel):
    use_embeddings: bool = False
    blend_weight: float = 0.5
    top_k_terms: int = 25
    skills_weight: float = 1.0
    terms_weight: float = 1.0

class ConfigUpdate(BaseModel):
    use_embeddings: Optional[bool] = None
    blend_weight: Optional[float] = None
    top_k_terms: Optional[int] = None
    skills_weight: Optional[float] = None
    terms_weight: Optional[float] = None
