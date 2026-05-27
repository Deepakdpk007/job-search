"""Company directory and per-company hiring stats."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Company, Job
from app.schemas import CompanyOut

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyOut])
async def list_companies(session: AsyncSession = Depends(get_session)) -> list[Company]:
    result = await session.execute(select(Company).order_by(Company.name))
    return list(result.scalars().all())


@router.get("/{slug}")
async def company_detail(slug: str, session: AsyncSession = Depends(get_session)) -> dict:
    result = await session.execute(select(Company).where(Company.slug == slug))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(404, "Company not found")

    counts = await session.execute(
        select(func.count(Job.id))
        .where(Job.company_id == company.id, Job.is_active.is_(True))
    )
    return {
        "company": CompanyOut.model_validate(company).model_dump(),
        "active_jobs": counts.scalar() or 0,
    }
