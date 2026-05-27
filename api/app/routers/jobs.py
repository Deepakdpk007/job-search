"""Job search and listing endpoints. Filters: city, skill, role, experience."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.models import Job, JobSkill, Location, Skill
from app.schemas import CompanyOut, JobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobOut])
async def list_jobs(
    city: str | None = Query(None),
    skill: str | None = Query(None),
    experience: str | None = Query(None, description="fresher | 1-3 | 3-5 | 5+"),
    employment_type: str | None = Query(None, description="full_time | intern | contract"),
    limit: int = Query(50, le=200),
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
) -> list[JobOut]:
    stmt = (
        select(Job)
        .options(
            selectinload(Job.company),
            selectinload(Job.location),
            selectinload(Job.skills).selectinload(JobSkill.skill),
        )
        .where(Job.is_active.is_(True))
        .order_by(Job.posted_at.desc().nulls_last())
        .limit(limit)
        .offset(offset)
    )
    if city:
        stmt = stmt.join(Location, Job.location_id == Location.id).where(Location.city == city)
    if experience:
        stmt = stmt.where(Job.experience_band == experience)
    if employment_type:
        stmt = stmt.where(Job.employment_type == employment_type)
    if skill:
        stmt = stmt.join(JobSkill).join(Skill).where(Skill.normalized == skill.lower())

    result = await session.execute(stmt)
    jobs = result.scalars().unique().all()

    return [
        JobOut(
            id=j.id,
            title=j.title,
            company=CompanyOut.model_validate(j.company),
            city=j.location.city if j.location else None,
            country=j.location.country if j.location else None,
            employment_type=j.employment_type,
            experience_band=j.experience_band,
            apply_url=j.apply_url,
            posted_at=j.posted_at,
            skills=[js.skill.name for js in j.skills],
        )
        for j in jobs
    ]
