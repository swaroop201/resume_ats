from typing import List, Optional
from dataclasses import dataclass
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class EngineResult:
    tfidf_scores: np.ndarray
    embed_scores: Optional[np.ndarray]

class ResumeScorer:
    def __init__(self, use_embeddings: bool = False):
        self.use_embeddings = use_embeddings
        self._embed_model = None
        if use_embeddings:
            try:
                from sentence_transformers import SentenceTransformer
                self._embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            except Exception:
                self._embed_model = None
                self.use_embeddings = False

    def _tfidf_scores(self, jd: str, resumes: List[str]) -> np.ndarray:
        vec = TfidfVectorizer(stop_words='english', max_features=20000)
        X = vec.fit_transform([jd] + resumes)
        jd_vec, res_mat = X[0:1], X[1:]
        sims = cosine_similarity(jd_vec, res_mat)[0]
        return sims

    def _embed_scores(self, jd: str, resumes: List[str]) -> Optional[np.ndarray]:
        if not self._embed_model:
            return None
        jd_emb = self._embed_model.encode([jd], normalize_embeddings=True)
        res_emb = self._embed_model.encode(resumes, normalize_embeddings=True)
        sims = (jd_emb @ res_emb.T).flatten()
        return sims

    def score(self, jd: str, resumes: List[str]) -> EngineResult:
        tfidf = self._tfidf_scores(jd, resumes)
        emb = self._embed_scores(jd, resumes) if self.use_embeddings else None
        return EngineResult(tfidf_scores=tfidf, embed_scores=emb)

    @staticmethod
    def blend(tfidf: np.ndarray, emb: Optional[np.ndarray], weight: float) -> np.ndarray:
        if emb is None:
            return tfidf
        w = float(max(0.0, min(1.0, weight)))
        return (1 - w) * tfidf + w * emb
