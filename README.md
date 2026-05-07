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
OPENAI_API_KEY=your_openai_api_key_here  # get from https://platform.openai.com/api-keys (active LLM provider)
GROQ_API_KEY=your_groq_api_key_here      # optional fallback — get from https://console.groq.com
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
| `OPENAI_API_KEY` | ✅ Yes | OpenAI API key for AI skill refinement (active provider, `gpt-4o-mini`) |
| `GROQ_API_KEY` | No | Groq API key — only required if you switch the refiner back to Groq |
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

The backend is designed to run as a single container on Cloud Run, with the frontend served separately from GitHub Pages. Local Docker testing → Cloud Run is **not zero-config**: skill files must move to GCS, the DB to Cloud SQL, and four code paths must be flipped from local-FS to GCS. Checklist below.

### Pre-deploy checklist

1. **Provision infra**
   - Cloud SQL Postgres instance (note the connection name `PROJECT:REGION:INSTANCE`).
   - GCS bucket for skill files.
   - Service account for the Cloud Run service with:
     - `roles/cloudsql.client` (DB connectivity)
     - `roles/storage.objectAdmin` on the bucket (skill file r/w + zip download)

2. **Flip storage code paths from local FS → GCS** in [`backend/app/services/repo_writer.py`](./backend/app/services/repo_writer.py)

   Four public functions each have a local-active line and a commented GCS block. **All four must be flipped** — otherwise upload will write to GCS but listing/preview/download will still try local disk and 404.

   | Function | Used by |
   |---|---|
   | `save_skill_to_repo()` | Upload route — writes `skill_card.json` + every uploaded file |
   | `list_skill_files()` | `GET /skills/{id}/files` — detail-modal file table |
   | `read_skill_file()` | `GET /skills/{id}/file?path=…` — file preview links |
   | `zip_skill()` | `GET /skills/{id}/download` — "Download ZIP" button |

   In each, comment the local return and uncomment the GCS block, e.g.:
   ```python
   # return _save_local(slug, files, skill)
   if settings.gcs_bucket:
       return _save_gcs(slug, files, skill)
   return _save_local(slug, files, skill)
   ```

3. **Set Cloud Run environment variables**
   ```
   APP_ENV=production
   GCS_BUCKET=<your-bucket>
   DATABASE_URL=postgresql+psycopg2://USER:PASS@/DBNAME?host=/cloudsql/PROJECT:REGION:INSTANCE
   SECRET_KEY=<random>
   GROQ_API_KEY=<key>           # or OPENAI_API_KEY if using OpenAI
   CORS_ORIGINS=https://sushanthtws.github.io
   ```
   Do **not** bake these into the image — Cloud Run injects them at runtime; `pydantic-settings` reads env vars directly when no `.env` is present.

4. **Run database migrations against Cloud SQL.** Two options:
   - **One-off (recommended):** start the Cloud SQL Auth Proxy locally, set `DATABASE_URL` to the proxy, run `alembic upgrade head`.
   - **Auto-on-start:** change the Dockerfile `CMD` to
     `sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"`.
     Alembic is idempotent so this is safe but adds a couple of seconds to every cold start.

5. **Deploy**
   ```bash
   gcloud run deploy synapse-backend \
     --source . \
     --region <region> \
     --add-cloudsql-instances PROJECT:REGION:INSTANCE \
     --service-account <service-account-email> \
     --allow-unauthenticated
   ```
   Cloud Run will build from the existing [`Dockerfile`](./Dockerfile), which already binds `0.0.0.0:$PORT`.

6. **Update frontend `config.js`** to point at the Cloud Run URL, and redeploy GitHub Pages:
   ```js
   const CONFIG = { API: "https://synapse-backend-xxxxx.a.run.app" };
   ```

### What does NOT need to change for Cloud Run

- [`Dockerfile`](./Dockerfile) — already binds `0.0.0.0:$PORT`.
- CORS middleware — driven by `CORS_ORIGINS`.
- The review wizard, anchor-tag UI, multi-file upload, artifact classifier — all backend-storage-agnostic.
- Auth, schemas, all routes other than the four `repo_writer` paths.

### To switch back to local disk

Reverse the four comment toggles in [`repo_writer.py`](./backend/app/services/repo_writer.py). DB and env vars stay the same.

### What gets written per skill

Each upload produces a folder `<base>/skills/<slug>/` (or `gs://<bucket>/skills/<slug>/` on GCS) containing:

| File | Purpose |
|---|---|
| `skill_card.json` | The structured AI-refined skill object (title, summary, tags, tools, etc.) |
| `<original-filename>.md` | The user's uploaded markdown file dumped **as-is**, preserving its original filename. Used as the source of truth for the skill body. |

If no original payload is supplied, a minimal `README.md` is generated from `title` + `summary` as a fallback.

### Skill upload: file vs folder

The UI exposes **two upload buttons**:

- **Upload File** — pick a single `.md` (e.g. `SKILL.md`). Used as-is.
- **Upload Folder** — pick a directory containing the skill's full bundle: `SKILL.md` (or `README.md`), templates, configs, slash-command definitions, hook scripts, MCP configs, etc. Every file is preserved verbatim under `data/skills_repo/<slug>/` (or `gs://<bucket>/skills/<slug>/`).

**One skill per upload.** If a folder contains multiple `SKILL.md` files (or, failing that, multiple `README.md` files at distinct paths), the upload is rejected with `400` and a message listing the offending files. Upload each skill folder separately.

The backend picks the **primary skill markdown** in this priority:

1. `skill.md` / `SKILL.md`
2. `readme.md` / `README.md`
3. The shallowest other `.md` file

The file *listing* is fed to the LLM so tags pick up sibling-file signals — e.g. a folder containing `templates/jira_ticket_template.md` will get the tag `jira` even if `SKILL.md` doesn't mention it.

### Artifact classification

Every uploaded file is classified by [`artifact_classifier.py`](./backend/app/services/artifact_classifier.py) into one of: `skill_doc`, `readme`, `claude_md`, `agents_md`, `cursor_rules`, `windsurf_rules`, `slash_command`, `subagent`, `hook`, `mcp_config`, `eval`, `prompt`, `template`, `doc`, `config`, `script`, `other`. The classification is stored in `skill_card.json` under `artifacts[]` and shown in the UI's skill detail modal so users (and downstream agents) can see what each file is for.

### Skill lifecycle: upload → review wizard → repository

After upload, the agent persists a **draft** (not yet in the public repository) and a 3-step review wizard opens in the UI:

1. **Review** — shows the agent's interpretation: title, description, *where to use*, *why to use*, *how to use* (numbered steps), and tags.
   - Click **Looks good →** to advance.
   - Click **Needs fixes** to open the edit form (title, summary, where/why/how, tags, tools, tech stack, languages). On save, the wizard returns to step 1 with the updated values. Edits hit `PATCH /api/v1/skills/{id}`.
2. **Usage** — *Is this skill currently in use?* If yes, pick a platform (Anthropic Claude Code, Claude.ai, Cursor, Windsurf, or *Other…* + free text).
3. **Confirm** — *Upload to repository?* Yes calls `PATCH /api/v1/skills/{id}/complete` with `{is_in_use, used_at}` payload, sets `is_complete=true`, locks the slug. Subsequent uploads of the same slug return `409 Skill already finalized`.

Closing the wizard or clicking *Save as draft & exit* leaves the skill as a draft. Re-uploading the same slug while still a draft overwrites the draft (handy while iterating).

### Skill detail view & download

Click any card to open a detail modal with: summary, key points, tags/tools, classified file list (each file links to its content), and a **Download ZIP** button that streams the full skill folder as `<slug>.zip`. New endpoints:

- `GET /api/v1/skills/{id}/files` — file listing with classified types
- `GET /api/v1/skills/{id}/file?path=...` — fetch a single file's contents
- `GET /api/v1/skills/{id}/download` — zip of the whole skill folder
- `PATCH /api/v1/skills/{id}/complete` — finalize a draft

All four work for both local FS and GCS (GCS branch commented in [`repo_writer.py`](./backend/app/services/repo_writer.py)).

### Marketplace UX: anchor tags & category pills

The frontend computes a tag-frequency map across all uploaded skills on every load:

- Tags appearing in **≥2 skills** are treated as **anchor tags** (rendered in solid blue chips, while singletons are faded grey). Anchor tags are the natural axes of the catalog — re-usable across skills.
- The top anchor tags become **category pills** above the grid. Clicking a pill filters the grid to skills carrying that tag; clicking again clears the filter.
- The keyword search scorer weights matches in `title` (×4), `tags`/`tools` (×3), and `summary` (×1), so a query like "jira" surfaces JIRA-tagged skills first.

This is intentionally rule-based and runs entirely in the browser — no extra LLM call, no DB columns. When the catalog grows large enough that frequency clustering stops being meaningful, we'll layer an LLM-driven hierarchical taxonomy on top (see commented design notes in [`refiner.py`](./backend/app/services/refiner.py)).

### Note: `difficulty` field removed

The `difficulty` field was removed from the skill schema, DB model, refiner output, and UI as of migration `002_drop_difficulty`. Run `alembic upgrade head` after pulling these changes.

---

## Switching the LLM provider (OpenAI ↔ Groq)

Skill refinement is handled by [`backend/app/services/refiner.py`](./backend/app/services/refiner.py). The active provider is **OpenAI** (`gpt-4o-mini`). A Groq (Llama 3) fallback is included as commented code so you can swap providers without rewriting the file.

**To switch from OpenAI → Groq:**

1. Ensure `GROQ_API_KEY` is set in `.env` (get one at https://console.groq.com).
2. Open `backend/app/services/refiner.py` and in `_get_client()`:
   - **Comment out** the OpenAI block:
     ```python
     # _client = OpenAI(api_key=settings.openai_api_key or "dummy")
     ```
   - **Uncomment** the Groq block:
     ```python
     _client = OpenAI(
         api_key=settings.groq_api_key or "dummy",
         base_url="https://api.groq.com/openai/v1",
     )
     ```
3. Toggle the `MODEL` constant just below — comment `gpt-4o-mini`, uncomment `llama-3.1-8b-instant`.
4. Restart the backend.

To switch back to OpenAI, reverse the toggles. The schema/prompt is shared between providers, so no other changes are needed.

> **Tip:** After swapping providers, clear stored skill files (`/tmp/skills/*` or `data/skills_repo/*`) and the DB (`DELETE /api/v1/reset-db`) before re-uploading, so you're comparing fresh outputs side by side.
