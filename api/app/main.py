"""FastAPI application entry point."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import companies, health, heatmap, jobs, trends

settings = get_settings()

app = FastAPI(
    title="Job Search Intelligence API",
    description="Hiring heatmaps, skill trends, and role analytics for India.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(jobs.router, prefix="/api")
app.include_router(companies.router, prefix="/api")
app.include_router(trends.router, prefix="/api")
app.include_router(heatmap.router, prefix="/api")
