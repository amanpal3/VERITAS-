"""
VERITAS - Main FastAPI Entrypoint
Initializes application, CORS middleware, Sentry error monitoring, lifespan events,
and router registrations.
"""
from contextlib import asynccontextmanager
import logging
import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import analytics, communities, entities, graph, health, paths
from backend.app.core.config import get_settings
from backend.app.core.exceptions import (
    VeritasAPIException,
    unhandled_exception_handler,
    veritas_exception_handler,
)
from backend.app.database.neo4j import neo4j_db
from backend.app.services.graph_service import graph_service

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("veritas.api")

settings = get_settings()

# Initialize Sentry Error Monitoring & Distributed Tracing
if settings.SENTRY_DSN:
    logger.info(f"Initializing Sentry error monitoring for environment '{settings.ENVIRONMENT}'...")
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        send_default_pii=False,
    )
else:
    logger.info("SENTRY_DSN not configured; continuing with local exception logging.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events: startup hydration and graceful shutdown."""
    logger.info("Executing VERITAS startup sequence...")
    # Hydrate graph and run initial algorithms
    graph_service.initialize()
    yield
    logger.info("Executing VERITAS shutdown sequence...")
    neo4j_db.close()


app = FastAPI(
    title="VERITAS Criminal Network Intelligence API",
    version=settings.VERSION,
    description="AI-powered graph analytics, suspect dossier tracking, and multi-hop intelligence for law enforcement.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Exception Handlers
app.add_exception_handler(VeritasAPIException, veritas_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# CORS Middleware - Development localhost & Production Render domain support
cors_origins = list(settings.CORS_ORIGINS)
if settings.FRONTEND_URL and settings.FRONTEND_URL not in cors_origins:
    cors_origins.append(settings.FRONTEND_URL.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://.*\.onrender\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
api_v1_prefix = settings.API_V1_STR

app.include_router(health.router, prefix=api_v1_prefix)
app.include_router(graph.router, prefix=api_v1_prefix)
app.include_router(entities.router, prefix=api_v1_prefix)
app.include_router(paths.router, prefix=api_v1_prefix)
app.include_router(communities.router, prefix=api_v1_prefix)
app.include_router(analytics.router, prefix=api_v1_prefix)

# Also mount at root for direct/proxied client compatibility
app.include_router(health.router, include_in_schema=False)
app.include_router(graph.router, include_in_schema=False)
app.include_router(entities.router, include_in_schema=False)
app.include_router(paths.router, include_in_schema=False)
app.include_router(communities.router, include_in_schema=False)
app.include_router(analytics.router, include_in_schema=False)


@app.get("/", summary="Root Welcome & Index", tags=["System Health"])
async def root():
    """System welcome and operational metadata."""
    return {
        "title": "VERITAS Criminal Network Intelligence API",
        "version": settings.VERSION,
        "docs": "/docs",
        "api_v1_base": api_v1_prefix,
        "status": "online",
    }
