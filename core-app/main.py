import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from config import settings
from db import engine

from routers import webhook

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Postgres — non-fatal on Day 1 local dev (no Docker) ──────────
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ Postgres connected")
    except Exception as exc:
        logger.warning(
            "⚠️  Postgres not reachable (%s). "
            "Start docker-compose or set DATABASE_URL. "
            "App will start but DB calls will fail.",
            exc,
        )

    # TODO Day 4: await init_redis()
    # TODO Day 4: await init_kafka()
    # TODO Day 4: asyncio.create_task(start_kafka_consumer())

    logger.info("🚀 AutoResolve Core App started")
    yield

    # ── Shutdown ─────────────────────────────────────────────────────
    await engine.dispose()
    # TODO Day 4: await close_redis()
    # TODO Day 4: await close_kafka()
    logger.info("👋 Shutdown complete")


app = FastAPI(
    title="AutoResolve",
    description="Autonomous CI/CD failure diagnosis and repair agent",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router)

# Routers are registered as each day is completed:
# TODO Day 2:  from routers.webhook import router as webhook_router
# TODO Day 2:  app.include_router(webhook_router, prefix="/api")
# TODO Day 16: from routers.dashboard import router as dashboard_router
# TODO Day 16: app.include_router(dashboard_router, prefix="/api")
# TODO Day 16: from routers.websocket import router as ws_router
# TODO Day 16: app.include_router(ws_router)
# TODO Day 16: from routers.health import router as health_router
# TODO Day 16: app.include_router(health_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "service": "AutoResolve",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "core-app"}