# Synapse Platform

Governed Multi-Repository Engineering Intelligence Graph.

---

## Prerequisites

Make sure these are installed on your system:

| Tool | Version | Install |
|---|---|---|
| Python | 3.11+ | https://python.org |
| Docker | latest | https://docker.com |
| Git | latest | https://git-scm.com |
| PostgreSQL client (optional) | any | for DB inspection |

---

## 1. Clone the repository

```bash
git clone https://github.com/sushanthtws/synapse-platform.git
cd synapse-platform
```

---

## 2. Create Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in the required values:

```dotenv
GROQ_API_KEY=your_groq_api_key_here      # get from https://console.groq.com
SECRET_KEY=any-random-secret-string
DATABASE_URL=postgresql://synapse:synapse_dev@localhost:5432/synapse
```

All other values can stay as defaults for local development.

---

## 5. Start PostgreSQL (Docker)

```bash
docker compose up postgres -d
```

Wait a few seconds for it to be healthy, then verify:

```bash
docker ps | grep postgres
# should show: (healthy)
```

---

## 6. Create database user & database

> Skip this step if using the Docker postgres from step 5 — it creates them automatically.
> Only needed if using a local Postgres installation.

```bash
psql postgresql://postgres@localhost:5432/postgres \
  -c "CREATE USER synapse WITH PASSWORD 'synapse_dev';"

psql postgresql://postgres@localhost:5432/postgres \
  -c "CREATE DATABASE synapse OWNER synapse;"
```

---

## 7. Run database migrations

```bash
cd backend
alembic upgrade head
cd ..
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial schema
```

---

## 8. Set up frontend config

```bash
cp frontend/config.example.js frontend/config.js
```

`frontend/config.js` is already set to `http://localhost:8080` — no changes needed for local dev.

---

## 9. Start the backend

```bash
source .venv/bin/activate
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

Verify at: http://localhost:8080/health → `{"status":"ok"}`

API docs at: http://localhost:8080/api/docs

---

## 10. Start the frontend *(new terminal tab)*

```bash
cd frontend
python3 -m http.server 3000
```

Open in browser: **http://localhost:3000**

---

## Project Structure

```
synapse-platform/
├── backend/                  ← FastAPI backend
│   ├── app/
│   │   ├── api/routes/       ← API endpoints
│   │   ├── core/config.py    ← settings (reads .env)
│   │   ├── db/               ← SQLAlchemy setup
│   │   ├── models/           ← DB models (Skill, User, Project)
│   │   ├── schemas/          ← Pydantic response schemas
│   │   ├── services/         ← refiner.py (Groq AI), repo_writer.py
│   │   ├── workers/          ← Celery tasks
│   │   └── main.py           ← FastAPI app entry point
│   └── alembic/              ← DB migrations
├── frontend/
│   ├── index.html            ← UI (served via python http.server / GitHub Pages)
│   ├── style.css
│   ├── config.js             ← API URL (gitignored, copy from config.example.js)
│   └── config.example.js
├── skills_repo/              ← uploaded skill files (gitignored)
├── .env                      ← secrets (gitignored, copy from .env.example)
├── .env.example              ← template for .env
├── docker-compose.yml        ← Postgres, Redis, Elasticsearch
├── Dockerfile                ← backend container
└── requirements.txt
```

---

## Quick Reference

| Service | URL | Start command |
|---|---|---|
| Frontend | http://localhost:3000 | `cd frontend && python3 -m http.server 3000` |
| Backend API | http://localhost:8080 | `cd backend && uvicorn app.main:app --port 8080 --reload` |
| Swagger Docs | http://localhost:8080/api/docs | (auto) |
| PostgreSQL | localhost:5432 | `docker compose up postgres -d` |

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Groq API key for AI skill refinement |
| `DATABASE_URL` | ✅ Yes | PostgreSQL connection string |
| `SECRET_KEY` | ✅ Yes | Session signing secret |
| `APP_ENV` | No | `development` (default) or `production` |
| `API_SECRET` | No | If set, protects admin endpoints with `X-API-Key` header |
| `CORS_ORIGINS` | No | Comma-separated allowed origins |
| `BASE_SKILL_DIR` | No | Local folder for skill files (dev only) |
| `GCS_BUCKET` | No | GCS bucket name (production only) |
| `REDIS_URL` | No | Redis URL for Celery workers |

---

## Deploying to GCP Cloud Run

See [DEPLOY_GCP.md](./DEPLOY_GCP.md) for full instructions.

Set these extra env vars on Cloud Run:
```
APP_ENV=production
GCS_BUCKET=your-gcs-bucket-name
DATABASE_URL=postgresql://user:pass@/dbname?host=/cloudsql/project:region:instance
```
