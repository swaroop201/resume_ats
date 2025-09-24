from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import config
from app.routers import analyze, config_routes, diagnose, webui

app = FastAPI(title="Resume Analyzer API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in config.allowed_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (CSS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/health")
async def health():
    return {"status": "ok"}

# APIs
app.include_router(analyze.router, prefix="/api")
app.include_router(config_routes.router, prefix="/api")
app.include_router(diagnose.router, prefix="/api")

# Web UI
app.include_router(webui.router)
