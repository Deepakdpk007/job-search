# Job Search — Hiring Intelligence for India

A platform that turns raw job postings into hiring intelligence: city heatmaps,
skill demand trends, hiring velocity, and role analytics. India-focused MVP.

## Status

MVP skeleton. Ingests from Greenhouse (one ATS) end-to-end as a vertical slice.
Lever, Ashby, and YC come after the data spine is proven.

## Stack

- **Frontend**: Next.js 15, TypeScript, Tailwind, shadcn/ui
- **Backend**: FastAPI (Python 3.11+), SQLAlchemy 2.0 async, Alembic
- **DB**: PostgreSQL 16
- **Ingestion**: httpx async client, scheduled via cron/Celery later

## Quick start

```bash
# 1. Start Postgres
docker compose up -d

# 2. Set up env
cp .env.example .env

# 3. Backend
cd api
python -m venv .venv && source .venv/bin/activate
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload

# 4. Run an ingestion (separate terminal)
cd api && source .venv/bin/activate
python -m app.ingestion.run --source greenhouse

# 5. Frontend (separate terminal)
cd web
npm install
npm run dev
```

API at http://localhost:8000 (docs at /docs).
Web at http://localhost:3000.

## Layout

```
api/      FastAPI service + ingestion workers
web/      Next.js frontend
```

See `api/app/ingestion/companies.yml` to add Greenhouse company slugs.

## Roadmap

- [x] Project scaffold
- [ ] Greenhouse ingestion end-to-end
- [ ] Skill extraction (rule-based → embeddings later)
- [ ] City heatmap UI
- [ ] Skill trends UI
- [ ] Lever + Ashby ingestion
- [ ] Daily cron / Celery beat
- [ ] Deploy: Vercel + Railway + Neon
