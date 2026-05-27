"""Greenhouse Job Boards API ingestion.

Public endpoint: https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true
Returns all jobs for a company; no auth needed.
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import re
from datetime import datetime
from html import unescape
from typing import Any

import httpx
from dateutil import parser as dateparser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.ingestion.normalizer import (
    classify_role,
    employment_type,
    experience_band,
    normalize_location,
)
from app.ingestion.skill_extractor import extract_skills
from app.models import Company, IngestionRun, Job, JobSkill, Location, Skill

log = logging.getLogger(__name__)
settings = get_settings()

GREENHOUSE_BASE = "https://boards-api.greenhouse.io/v1/boards"
_HTML_TAG = re.compile(r"<[^>]+>")


def _strip_html(html: str) -> str:
    return unescape(_HTML_TAG.sub(" ", html or "")).strip()


async def _fetch_company_jobs(client: httpx.AsyncClient, slug: str) -> list[dict[str, Any]]:
    """Fetch all jobs for a Greenhouse company slug, with retries."""
    url = f"{GREENHOUSE_BASE}/{slug}/jobs"
    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError,)),
        reraise=True,
    ):
        with attempt:
            resp = await client.get(url, params={"content": "true"})
            resp.raise_for_status()
            return resp.json().get("jobs", [])
    return []


def _content_hash(payload: dict[str, Any]) -> str:
    """Stable hash for dedup / change detection."""
    parts = [
        str(payload.get("id", "")),
        payload.get("title", "") or "",
        payload.get("location", {}).get("name", "") or "",
        payload.get("updated_at", "") or "",
    ]
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


async def _get_or_create_location(session: AsyncSession, raw: str) -> Location | None:
    if not raw:
        return None
    existing = await session.execute(select(Location).where(Location.raw_text == raw))
    loc = existing.scalar_one_or_none()
    if loc:
        return loc
    norm = normalize_location(raw)
    loc = Location(
        raw_text=raw,
        city=norm.city,
        country=norm.country,
        is_remote=norm.is_remote,
    )
    session.add(loc)
    await session.flush()
    return loc


async def _get_or_create_skill(session: AsyncSession, name: str) -> Skill:
    normalized = name.lower()
    existing = await session.execute(select(Skill).where(Skill.normalized == normalized))
    skill = existing.scalar_one_or_none()
    if skill:
        return skill
    skill = Skill(name=name, normalized=normalized)
    session.add(skill)
    await session.flush()
    return skill


async def _upsert_job(
    session: AsyncSession,
    company: Company,
    payload: dict[str, Any],
) -> tuple[bool, bool]:
    """Insert or update a single job. Returns (inserted, updated)."""
    external_id = str(payload["id"])
    title = payload.get("title", "").strip()
    location_raw = (payload.get("location") or {}).get("name", "")
    description = _strip_html(payload.get("content", "") or "")
    apply_url = payload.get("absolute_url")
    posted_at_raw = payload.get("updated_at") or payload.get("first_published")
    posted_at: datetime | None = None
    if posted_at_raw:
        try:
            posted_at = dateparser.parse(posted_at_raw)
        except (ValueError, TypeError):
            posted_at = None

    chash = _content_hash(payload)

    existing_q = await session.execute(
        select(Job).where(Job.ats_source == "greenhouse", Job.external_id == external_id)
    )
    existing = existing_q.scalar_one_or_none()

    location = await _get_or_create_location(session, location_raw)
    job_text = f"{title}\n{description}"
    skill_names = extract_skills(job_text)

    if existing:
        existing.last_seen_at = datetime.utcnow()
        existing.is_active = True
        if existing.content_hash == chash:
            return False, False
        existing.title = title
        existing.title_normalized = title.lower()
        existing.description = description
        existing.apply_url = apply_url
        existing.posted_at = posted_at
        existing.location_id = location.id if location else None
        existing.experience_band = experience_band(title, description)
        existing.employment_type = employment_type(title, payload)
        existing.content_hash = chash
        existing.raw = payload
        # Refresh skills
        existing.skills.clear()
        await session.flush()
        for skill_name in skill_names:
            skill = await _get_or_create_skill(session, skill_name)
            session.add(JobSkill(job_id=existing.id, skill_id=skill.id))
        return False, True

    job = Job(
        external_id=external_id,
        ats_source="greenhouse",
        company_id=company.id,
        location_id=location.id if location else None,
        title=title,
        title_normalized=title.lower(),
        description=description,
        apply_url=apply_url,
        posted_at=posted_at,
        experience_band=experience_band(title, description),
        employment_type=employment_type(title, payload),
        content_hash=chash,
        raw=payload,
    )
    # Role classification stored in raw for now; category_id wiring is Phase 2.
    _ = classify_role(title)
    session.add(job)
    await session.flush()
    for skill_name in skill_names:
        skill = await _get_or_create_skill(session, skill_name)
        session.add(JobSkill(job_id=job.id, skill_id=skill.id))
    return True, False


async def _get_or_create_company(session: AsyncSession, slug: str, name: str, hq: str | None) -> Company:
    existing = await session.execute(select(Company).where(Company.slug == slug))
    company = existing.scalar_one_or_none()
    if company:
        return company
    company = Company(slug=slug, name=name, ats_source="greenhouse", hq_country=hq)
    session.add(company)
    await session.flush()
    return company


async def ingest_companies(session: AsyncSession, companies: list[dict[str, Any]]) -> dict[str, int]:
    """Ingest a list of company dicts (slug, name, hq_country). Returns counters."""
    run = IngestionRun(source="greenhouse")
    session.add(run)
    await session.flush()

    counters = {"seen": 0, "inserted": 0, "updated": 0}
    sem = asyncio.Semaphore(settings.ingestion_concurrency)

    headers = {"User-Agent": settings.ingestion_user_agent}
    timeout = httpx.Timeout(settings.ingestion_request_timeout)

    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
        async def _process_one(entry: dict[str, Any]) -> None:
            slug = entry["slug"]
            name = entry.get("name", slug)
            hq = entry.get("hq_country")
            async with sem:
                try:
                    payloads = await _fetch_company_jobs(client, slug)
                except httpx.HTTPError as e:
                    log.warning("greenhouse fetch failed for %s: %s", slug, e)
                    return
                company = await _get_or_create_company(session, slug, name, hq)
                for payload in payloads:
                    counters["seen"] += 1
                    inserted, updated = await _upsert_job(session, company, payload)
                    counters["inserted"] += int(inserted)
                    counters["updated"] += int(updated)
                await session.commit()
                log.info("greenhouse %s: %d postings processed", slug, len(payloads))

        await asyncio.gather(*(_process_one(e) for e in companies))

    run.finished_at = datetime.utcnow()
    run.status = "success"
    run.jobs_seen = counters["seen"]
    run.jobs_inserted = counters["inserted"]
    run.jobs_updated = counters["updated"]
    await session.commit()
    return counters
