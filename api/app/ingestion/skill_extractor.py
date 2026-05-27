"""Rule-based skill extraction. Replace with NER + embeddings in Phase 2."""
from __future__ import annotations

import re

# Curated skill dictionary. Phase 2: load from DB / managed taxonomy.
SKILLS: dict[str, str] = {
    # Languages
    "python": "Python",
    "java": "Java",
    "kotlin": "Kotlin",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "c++": "C++",
    "scala": "Scala",
    "swift": "Swift",
    "ruby": "Ruby",
    # Frontend
    "react": "React",
    "next.js": "Next.js",
    "nextjs": "Next.js",
    "vue": "Vue",
    "angular": "Angular",
    "tailwind": "Tailwind",
    # Backend / frameworks
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "spring": "Spring",
    "spring boot": "Spring Boot",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "express": "Express",
    # Data / ML
    "kafka": "Kafka",
    "spark": "Spark",
    "airflow": "Airflow",
    "snowflake": "Snowflake",
    "databricks": "Databricks",
    "dbt": "dbt",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "scikit-learn": "scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "huggingface": "HuggingFace",
    "langchain": "LangChain",
    "llm": "LLMs",
    "genai": "GenAI",
    # Cloud / infra
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "docker": "Docker",
    "terraform": "Terraform",
    # DB
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "elasticsearch": "Elasticsearch",
}

# Compile a regex per token for word-boundary matches.
_PATTERNS = [
    (re.compile(rf"(?<![A-Za-z0-9+#.]){re.escape(token)}(?![A-Za-z0-9+#.])", re.IGNORECASE), display)
    for token, display in SKILLS.items()
]


def extract_skills(text: str) -> list[str]:
    """Return canonical skill names found in text. De-duplicated, order-preserving."""
    if not text:
        return []
    seen: dict[str, None] = {}
    for pattern, display in _PATTERNS:
        if pattern.search(text):
            seen[display] = None
    return list(seen.keys())
