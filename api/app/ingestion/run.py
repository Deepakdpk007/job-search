"""CLI entrypoint for ingestion.

Usage:
    python -m app.ingestion.run --source greenhouse
    python -m app.ingestion.run --source greenhouse --rollup
"""
from __future__ import annotations

import argparse
import asyncio
import logging
from datetime import date
from pathlib import Path

import yaml
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionLocal
from app.ingestion.greenhouse import ingest_companies as ingest_greenhouse
from app.models import Job, JobSkill, Location, Skill, Trend

CONFIG = Path(__file__).parent / "companies.yml"


def _load_config() -> dict:
    with CONFIG.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


async def _rollup_today(session: AsyncSession) -> int:
    """Compute today's per-skill and per-city counts. Idempotent."""
    today = date.today()
    await session.execute(delete(Trend).where(Trend.bucket_date == today))

    # Skill counts
    skill_q = (
        select(Skill.name, func.count(JobSkill.job_id))
        .join(JobSkill, JobSkill.skill_id == Skill.id)
        .join(Job, Job.id == JobSkill.job_id)
        .where(Job.is_active.is_(True))
        .group_by(Skill.name)
    )
    rows = (await session.execute(skill_q)).all()
    for name, count in rows:
        session.add(Trend(bucket_date=today, dimension="skill", dimension_key=name, job_count=count))

    # City counts
    city_q = (
        select(Location.city, func.count(Job.id))
        .join(Job, Job.location_id == Location.id)
        .where(Job.is_active.is_(True), Location.city.is_not(None))
        .group_by(Location.city)
    )
    rows = (await session.execute(city_q)).all()
    for city, count in rows:
        session.add(Trend(bucket_date=today, dimension="city", dimension_key=city, job_count=count))

    await session.commit()
    return len(rows)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="greenhouse", choices=["greenhouse"])
    parser.add_argument("--rollup", action="store_true", help="Recompute trend rollups after ingest")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    config = _load_config()

    async with SessionLocal() as session:
        if args.source == "greenhouse":
            companies = config.get("greenhouse", []) or []
            if not companies:
                print("No companies configured under greenhouse: in companies.yml")
                return
            counters = await ingest_greenhouse(session, companies)
            print(f"greenhouse: seen={counters['seen']} inserted={counters['inserted']} updated={counters['updated']}")

        if args.rollup:
            n = await _rollup_today(session)
            print(f"rollup: wrote {n} trend rows for {date.today()}")


if __name__ == "__main__":
    asyncio.run(main())
