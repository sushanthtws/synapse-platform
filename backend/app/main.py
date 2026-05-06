"""
Synapse — FastAPI application entry point.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import (
    analytics,
    auth,
    chat,
    compare,
    jobs,
    leaderboard,
    projects,
    skills,
    validations,
    webhooks,
)
from app.core.config import settings
from app.db.base import engine, Base

log = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("synapse.startup", env=settings.app_env)
    Base.metadata.create_all(bind=engine)
    yield
    log.info("synapse.shutdown")


app = FastAPI(
    title="Synapse",
    description="Governed Multi-Repository Engineering Intelligence Graph",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── Middleware ─────────────────────────────────────────────────────────────────

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, https_only=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────

API_PREFIX = "/api/v1"

app.include_router(auth.router,        prefix=API_PREFIX)
app.include_router(skills.router,      prefix=API_PREFIX)
app.include_router(projects.router,    prefix=API_PREFIX)
app.include_router(validations.router, prefix=API_PREFIX)
app.include_router(leaderboard.router, prefix=API_PREFIX)
app.include_router(analytics.router,   prefix=API_PREFIX)
app.include_router(compare.router,     prefix=API_PREFIX)
app.include_router(chat.router,        prefix=API_PREFIX)
app.include_router(jobs.router,        prefix=API_PREFIX)
app.include_router(webhooks.router,    prefix=API_PREFIX)


@app.get("/health", tags=["ops"])
async def health():
    return {"status": "ok"}
