"""Normalize raw posting fields: city, role category, experience band, employment type."""
from __future__ import annotations

import re
from dataclasses import dataclass

# Indian metro normalization. Extend as needed.
INDIAN_CITY_ALIASES: dict[str, str] = {
    "bengaluru": "Bengaluru",
    "bangalore": "Bengaluru",
    "blr": "Bengaluru",
    "hyderabad": "Hyderabad",
    "hyd": "Hyderabad",
    "chennai": "Chennai",
    "madras": "Chennai",
    "mumbai": "Mumbai",
    "bombay": "Mumbai",
    "pune": "Pune",
    "gurgaon": "Gurgaon",
    "gurugram": "Gurgaon",
    "noida": "Noida",
    "delhi": "Delhi",
    "new delhi": "Delhi",
    "ncr": "Delhi NCR",
    "kolkata": "Kolkata",
    "ahmedabad": "Ahmedabad",
    "kochi": "Kochi",
    "thiruvananthapuram": "Thiruvananthapuram",
    "trivandrum": "Thiruvananthapuram",
    "jaipur": "Jaipur",
    "indore": "Indore",
    "coimbatore": "Coimbatore",
}

REMOTE_KEYWORDS = ("remote", "anywhere", "wfh", "work from home")


@dataclass(slots=True)
class NormalizedLocation:
    raw: str
    city: str | None
    country: str | None
    is_remote: bool


def normalize_location(raw: str | None) -> NormalizedLocation:
    if not raw:
        return NormalizedLocation("", None, None, False)
    low = raw.strip().lower()
    is_remote = any(k in low for k in REMOTE_KEYWORDS)

    # Try exact alias match first
    for token in re.split(r"[,/|;]| - ", low):
        token = token.strip()
        if token in INDIAN_CITY_ALIASES:
            return NormalizedLocation(raw=raw, city=INDIAN_CITY_ALIASES[token], country="India", is_remote=is_remote)

    # Heuristic: any alias substring
    for alias, canonical in INDIAN_CITY_ALIASES.items():
        if alias in low:
            return NormalizedLocation(raw=raw, city=canonical, country="India", is_remote=is_remote)

    # Country guess: if "india" mentioned without a city we still tag country
    country = "India" if "india" in low else None
    return NormalizedLocation(raw=raw, city=None, country=country, is_remote=is_remote)


# Role classification (rule-based MVP; replace with embeddings later).
ROLE_RULES: list[tuple[str, list[str]]] = [
    ("ML/AI", ["machine learning", "ml engineer", "ai engineer", "deep learning", "nlp", "computer vision", "genai"]),
    ("Data Engineering", ["data engineer", "data platform", "etl", "kafka", "snowflake", "databricks"]),
    ("Data Science", ["data scientist", "analytics engineer"]),
    ("Backend", ["backend", "back-end", "back end", "server", "platform engineer", "api engineer"]),
    ("Frontend", ["frontend", "front-end", "front end", "react", "ui engineer", "web engineer"]),
    ("Mobile", ["android", "ios", "mobile engineer", "react native", "flutter"]),
    ("DevOps/SRE", ["devops", "sre", "site reliability", "infrastructure engineer", "platform sre"]),
    ("Security", ["security engineer", "appsec", "infosec"]),
    ("QA", ["qa engineer", "test engineer", "sdet", "quality engineer"]),
    ("Embedded", ["embedded", "firmware", "rtos"]),
    ("Fullstack", ["fullstack", "full-stack", "full stack"]),
]


def classify_role(title: str) -> str | None:
    low = title.lower()
    for category, keywords in ROLE_RULES:
        if any(k in low for k in keywords):
            return category
    return None


def experience_band(title: str, description: str | None = None) -> str | None:
    text = f"{title} {description or ''}".lower()
    if any(k in text for k in ("intern", "internship")):
        return "intern"
    if any(k in text for k in ("fresher", "graduate", "entry level", "entry-level", "0-1 year", "0 - 1")):
        return "fresher"
    if any(k in text for k in ("junior", "1-3 year", "1 - 3", "associate")):
        return "1-3"
    if any(k in text for k in ("senior", "sr.", "5+ year", "5 + year", "lead engineer")):
        return "5+"
    if any(k in text for k in ("staff", "principal", "architect")):
        return "5+"
    if any(k in text for k in ("3-5 year", "3 - 5", "mid-level", "mid level")):
        return "3-5"
    return None


def employment_type(title: str, raw: dict) -> str | None:
    low = title.lower()
    if "intern" in low:
        return "intern"
    if "contract" in low or "contractor" in low:
        return "contract"
    return "full_time"
