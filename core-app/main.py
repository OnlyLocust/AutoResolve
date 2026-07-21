import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from config import settings
from db import engine
from routers import webhook

# --- DAY 4 IMPORTS ---
from redis_client import init_redis, close_redis
from kafka_setup import create_kafka_topic
from services.kafka_producer import start_producer, stop_producer
from services.kafka_consumer import start_consumer, stop_consumer
# ---------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Postgres ──────────
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

    # ── Day 4: Redis & Kafka Startup ──────────
    try:
        await init_redis()
        logger.info("✅ Redis connected")
        
        await create_kafka_topic()
        await start_producer()
        await start_consumer()
        logger.info("✅ Kafka Producer & Consumer started")
    except Exception as exc:
        logger.warning(f"⚠️ Redis or Kafka startup failed: {exc}")

    logger.info("🚀 AutoResolve Core App started")
    yield

    # ── Shutdown ─────────────────────────────────────────────────────
    await engine.dispose()
    
    # ── Day 4: Redis & Kafka Shutdown ──────────
    try:
        await stop_consumer()
        await stop_producer()
        await close_redis()
    except Exception as exc:
        logger.warning(f"⚠️ Error during Redis/Kafka shutdown: {exc}")
        
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