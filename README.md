# LuminOS — MVP

The AI operating system for entrepreneurs. See `luminos-architecture.md`
(shared separately) for the full technical plan this implements.

## What's included

- **Backend** (`/backend`): FastAPI + SQLAlchemy + PostgreSQL, JWT auth,
  an AI provider abstraction (OpenAI today, swappable), a typed memory
  layer, and services for onboarding, tasks, business builder, health
  score, CEO briefing, and the AI assistant.
- **Frontend** (`/frontend`): Next.js 14 (App Router) + TypeScript +
  Tailwind. Auth pages, a 3-step onboarding flow, the command-center
  dashboard, and pages for every module in the nav.

## Running locally (Docker — recommended)

1. Copy env files and fill in your OpenAI key:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   # edit backend/.env and set OPENAI_API_KEY, SECRET_KEY
   ```
2. Start everything:
   ```bash
   docker compose up --build
   ```
3. The first boot runs `alembic upgrade head` automatically. Since no
   migration has been generated yet, generate the initial one first:
   ```bash
   docker compose run --rm backend alembic revision --autogenerate -m "initial schema"
   docker compose up --build
   ```
4. Visit:
   - Frontend: http://localhost:3000
   - Backend docs (Swagger): http://localhost:8000/docs
   - Health check: http://localhost:8000/health

## Running locally (without Docker)

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in values; point DATABASE_URL at a local Postgres
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Testing

```bash
cd backend
pytest tests/unit
```
(Integration tests that hit a real database go in `tests/integration` —
none are included yet; they'd need a test database fixture wired into
`conftest.py`.)

## Project layout

See the architecture document for the full annotated folder structure,
database schema (11 tables, relationships, indexes), API route list,
and the AI provider abstraction design. In short:

```
backend/app/
  core/         settings, security, logging, exceptions
  models/       SQLAlchemy models (one file per table)
  schemas/      Pydantic request/response models
  api/v1/       route handlers, one file per resource
  services/     business logic (incl. services/ai/ = the AI layer)
  repositories/ DB query layer
  dependencies/ FastAPI dependencies (auth, db session)

frontend/
  app/          Next.js routes (App Router)
  components/   ui/, dashboard/, onboarding/, assistant/, layout/
  hooks/        client-side data hooks
  lib/          api client, types, auth helpers
```

## Known gaps in this MVP pass (by design, not oversight)

- No migration files are pre-generated — run `alembic revision
  --autogenerate` once against a live Postgres so the migration matches
  whatever version of the models you're running.
- No automated integration tests yet (unit tests for auth/security only).
- Rate limiting on AI-calling endpoints is called out in the
  architecture doc but not yet implemented — add it at the FastAPI
  dependency level (e.g. `slowapi`) before any public deployment.
- The Health Score's marketing/customer-growth/financial sub-scores are
  intentionally simple placeholders (stage + declared-challenges based)
  until dedicated tracking (CRM data, ad spend, etc.) exists — see the
  comment in `health_score_service.py`.
