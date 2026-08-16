"""
FastAPI application — entry point.
Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title="Cofounder AI — Backend",
    version="0.1.0",
    description="AI-Agent System for Startup Automation",
)

# ── CORS ────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health probe ────────────────────────────────────────────────────────
@app.get("/health", tags=["ops"])
async def health_check():
    """Trivial liveness probe — returns 200 if the server is up."""
    return {"status": "ok"}
