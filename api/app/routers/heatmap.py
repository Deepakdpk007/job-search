"""City hiring heatmap aggregates."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Job, JobSkill, Location, Skill
from app.schemas import CityHeat

router = APIRouter(prefix="/heatmap", tags=["heatmap"])


@router.get("/cities", response_model=list[CityHeat])
async def city_heatmap(session: AsyncSession = Depends(get_session)) -> list[CityHeat]:
    counts_stmt = (
        select(Location.city, func.count(Job.id).label("n"))
        .join(Job, Job.location_id == Location.id)
        .where(Job.is_active.is_(True), Location.city.is_not(None))
        .group_by(Location.city)
        .order_by(func.count(Job.id).desc())
    )
    rows = (await session.execute(counts_stmt)).all()

    out: list[CityHeat] = []
    for city, n in rows:
        skills_stmt = (
            select(Skill.name, func.count(JobSkill.job_id).label("c"))
            .join(JobSkill, JobSkill.skill_id == Skill.id)
            .join(Job, Job.id == JobSkill.job_id)
            .join(Location, Location.id == Job.location_id)
            .where(Location.city == city, Job.is_active.is_(True))
            .group_by(Skill.name)
            .order_by(func.count(JobSkill.job_id).desc())
            .limit(8)
        )
        skills = [s for s, _ in (await session.execute(skills_stmt)).all()]
        out.append(CityHeat(city=city, job_count=n, top_skills=skills))
    return out
