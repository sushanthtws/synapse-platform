# Deploy Backend to Google Cloud Run

This backend is a FastAPI app and can be deployed directly to **Cloud Run**.

## 1) Prerequisites
- Google Cloud project with billing enabled
- `gcloud` CLI installed and authenticated
- APIs enabled:
  - Cloud Run API
  - Artifact Registry API
  - Cloud Build API

## 2) Set project variables
```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="asia-south1"
export SERVICE_NAME="synapse-backend"
```

## 3) Configure gcloud and enable APIs
```bash
gcloud auth login
gcloud config set project "$PROJECT_ID"
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
```

## 4) Deploy from source (uses Dockerfile)
Run this from repository root (`synapse-platform/`):

```bash
gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GROQ_API_KEY="your_groq_api_key",DB_NAME="/tmp/skills.db",BASE_SKILL_DIR="/tmp/skills"
```

After deployment, Cloud Run prints a service URL.
Use it as your frontend API base URL (for GitHub Pages frontend).

## 5) Update frontend API URL
If your frontend calls `http://localhost:8000`, replace it with your Cloud Run URL, for example:

```text
https://synapse-backend-xxxxx-uc.a.run.app
```

## Notes
- `DB_NAME` and `BASE_SKILL_DIR` default to `/tmp` in this repo for Cloud Run compatibility.
- `/tmp` is ephemeral; data is not durable across instance restarts.
- For persistent production storage, migrate from SQLite/files to Cloud SQL + Cloud Storage.
