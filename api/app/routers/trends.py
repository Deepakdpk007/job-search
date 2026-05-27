"""Skill demand trends. Reads from the Trend rollup table."""
from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Trend
from app.schemas import SkillTrend, TrendPoint

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("/skills", response_model=list[SkillTrend])
async def skill_trends(
    days: int = Query(30, ge=7, le=180),
    top: int = Query(20, le=100),
    session: AsyncSession = Depends(get_session),
) -> list[SkillTrend]:
    since = date.today() - timedelta(days=days)
    stmt = (
        select(Trend)
        .where(Trend.dimension == "skill", Trend.bucket_date >= since)
        .order_by(Trend.bucket_date)
    )
    rows = (await session.execute(stmt)).scalars().all()

    by_skill: dict[str, list[Trend]] = {}
    for r in rows:
        by_skill.setdefault(r.dimension_key, []).append(r)

    trends: list[SkillTrend] = []
    for skill_key, points in by_skill.items():
        total = sum(p.job_count for p in points)
        # Naive growth: last 7 days vs prior 7 days
        recent = [p for p in points if p.bucket_date >= date.today() - timedelta(days=7)]
        prior = [
            p for p in points
            if date.today() - timedelta(days=14) <= p.bucket_date < date.today() - timedelta(days=7)
        ]
        growth: float | None = None
        if prior:
            r_sum = sum(p.job_count for p in recent)
            p_sum = sum(p.job_count for p in prior)
            if p_sum:
                growth = round(((r_sum - p_sum) / p_sum) * 100, 1)
        trends.append(
            SkillTrend(
                skill=skill_key,
                total=total,
                points=[TrendPoint(bucket_date=p.bucket_date, job_count=p.job_count) for p in points],
                growth_pct_30d=growth,
            )
        )
    trends.sort(key=lambda t: t.total, reverse=True)
    return trends[:top]
