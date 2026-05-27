"""Pydantic response schemas for the API."""
from __future__ import annotations

from datetime import datetime, date

from pydantic import BaseModel, ConfigDict


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    name: str
    ats_source: str
    website: str | None = None


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    company: CompanyOut
    city: str | None = None
    country: str | None = None
    employment_type: str | None = None
    experience_band: str | None = None
    apply_url: str | None = None
    posted_at: datetime | None = None
    skills: list[str] = []


class TrendPoint(BaseModel):
    bucket_date: date
    job_count: int


class SkillTrend(BaseModel):
    skill: str
    points: list[TrendPoint]
    total: int
    growth_pct_30d: float | None = None


class CityHeat(BaseModel):
    city: str
    job_count: int
    top_skills: list[str] = []
    top_roles: list[str] = []
