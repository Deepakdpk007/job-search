"""SQLAlchemy ORM models. All eight core entities live here for MVP simplicity."""
from __future__ import annotations

from datetime import datetime, date

from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    ats_source: Mapped[str] = mapped_column(String(32))  # greenhouse | lever | ashby ...
    website: Mapped[str | None] = mapped_column(String(255))
    hq_country: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    jobs: Mapped[list["Job"]] = relationship(back_populates="company")


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    raw_text: Mapped[str] = mapped_column(String(255), index=True)
    city: Mapped[str | None] = mapped_column(String(128), index=True)
    region: Mapped[str | None] = mapped_column(String(128))
    country: Mapped[str | None] = mapped_column(String(64), index=True)
    is_remote: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (UniqueConstraint("raw_text", name="uq_location_raw_text"),)


class Category(Base):
    """Role taxonomy (Backend, Frontend, Data Eng, ML, DevOps, etc.)."""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    normalized: Mapped[str] = mapped_column(String(64), index=True)
    family: Mapped[str | None] = mapped_column(String(64))  # language | framework | cloud ...


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(128), index=True)
    ats_source: Mapped[str] = mapped_column(String(32), index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))

    title: Mapped[str] = mapped_column(String(255), index=True)
    title_normalized: Mapped[str] = mapped_column(String(255), index=True)
    department: Mapped[str | None] = mapped_column(String(128))
    employment_type: Mapped[str | None] = mapped_column(String(32))  # full_time | intern ...
    experience_band: Mapped[str | None] = mapped_column(String(32), index=True)  # fresher | 1-3 ...
    description: Mapped[str | None] = mapped_column(Text)
    apply_url: Mapped[str | None] = mapped_column(String(512))

    posted_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)

    content_hash: Mapped[str] = mapped_column(String(64), index=True)  # for dedup
    raw: Mapped[dict] = mapped_column(JSON)

    company: Mapped[Company] = relationship(back_populates="jobs")
    location: Mapped[Location | None] = relationship()
    skills: Mapped[list["JobSkill"]] = relationship(back_populates="job", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("ats_source", "external_id", name="uq_job_source_external_id"),
    )


class JobSkill(Base):
    __tablename__ = "job_skills"

    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)

    job: Mapped[Job] = relationship(back_populates="skills")
    skill: Mapped[Skill] = relationship()


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(32), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
    jobs_seen: Mapped[int] = mapped_column(Integer, default=0)
    jobs_inserted: Mapped[int] = mapped_column(Integer, default=0)
    jobs_updated: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(32), default="running")  # running | success | failed
    error: Mapped[str | None] = mapped_column(Text)


class Trend(Base):
    """Daily materialized aggregates. Populated by a rollup job; powers fast charts."""
    __tablename__ = "trends"

    id: Mapped[int] = mapped_column(primary_key=True)
    bucket_date: Mapped[date] = mapped_column(Date, index=True)
    dimension: Mapped[str] = mapped_column(String(32), index=True)  # skill | city | role | company
    dimension_key: Mapped[str] = mapped_column(String(128), index=True)
    job_count: Mapped[int] = mapped_column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("bucket_date", "dimension", "dimension_key", name="uq_trend_bucket"),
    )
