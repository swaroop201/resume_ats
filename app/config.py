import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class AppConfig(BaseModel):
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")
    use_embeddings: bool = os.getenv("USE_EMBEDDINGS", "false").lower() == "true"
    blend_weight: float = float(os.getenv("BLEND_WEIGHT", 0.5))
    top_k_terms: int = 25
    skills_weight: float = 1.0
    terms_weight: float = 1.0

config = AppConfig()
