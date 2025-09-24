from fastapi import APIRouter
from app.schemas import ConfigModel, ConfigUpdate
from app.config import config as live_config, AppConfig

router = APIRouter(prefix="/config", tags=["config"])

@router.get("/", response_model=ConfigModel)
def get_config():
    return ConfigModel(
        use_embeddings=live_config.use_embeddings,
        blend_weight=live_config.blend_weight,
        top_k_terms=live_config.top_k_terms,
        skills_weight=live_config.skills_weight,
        terms_weight=live_config.terms_weight,
    )

@router.put("/", response_model=ConfigModel)
def update_config(update: ConfigUpdate):
    data = live_config.model_dump()
    for k, v in update.model_dump(exclude_none=True).items():
        data[k] = v
    newc = AppConfig(**data)
    from app import config as cfg_module
    cfg_module.config = newc
    return ConfigModel(
        use_embeddings=newc.use_embeddings,
        blend_weight=newc.blend_weight,
        top_k_terms=newc.top_k_terms,
        skills_weight=newc.skills_weight,
        terms_weight=newc.terms_weight,
    )
