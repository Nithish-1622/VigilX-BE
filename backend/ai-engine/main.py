from __future__ import annotations
import socket
if not hasattr(socket, 'EAI_ADDRFAMILY'):
    socket.EAI_ADDRFAMILY = getattr(socket, 'EAI_FAMILY', 2)
from typing import Any

from contextlib import asynccontextmanager

# pyrefly: ignore [missing-import]
from fastapi import FastAPI

from routers.ask import router as ask_router
from utils.config import settings
from utils.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

import sys
import os
# Add the backend root so we can import the database adapter
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

# Lazy-load database adapter registry on demand to ensure instant server boot time


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    if os.getenv("DATABASE_URL"):
        try:
            import django
            from django.core.management import call_command
            call_command("migrate", "--noinput")
            logger.info("Django database migrations completed successfully.")
        except Exception as e:
            logger.warning("Django migration check skipped/failed: %s", e)
    yield
    logger.info("Stopping %s", settings.app_name)


# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
	title=settings.app_name,
	version=settings.app_version,
	lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip().rstrip('/') for origin in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000").split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers.ask import router as ask_router
from routers.voice import router as voice_router
from routers.history import router as history_router
from routers.documents import router as documents_router
from routers.graph import router as graph_router
from routers.profiling import router as profiling_router
# V2 Multi-Agent Investigation Intelligence Platform
# V1 /ai/ask is PRESERVED — V2 adds /ai/v2/ask (temporary dev namespace)
from routers.ask_v2 import router as ask_v2_router

app.include_router(ask_router)
app.include_router(voice_router)
app.include_router(history_router)
app.include_router(documents_router)
app.include_router(graph_router)
app.include_router(profiling_router)
app.include_router(ask_v2_router)

# Mount Django WSGI Application on /api and /admin for single-process deployment
from a2wsgi import WSGIMiddleware
django_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "django-api"))
if django_dir not in sys.path:
    sys.path.insert(0, django_dir)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
try:
    import django
    django.setup()
    from config.wsgi import application as django_app
    app.mount("/api", WSGIMiddleware(django_app))
    app.mount("/admin", WSGIMiddleware(django_app))
    logger.info("Successfully mounted Django REST API on /api and /admin")
except Exception as e:
    logger.error("Failed to mount Django app: %s", e)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "status": "success",
        "message": "Welcome to VigilX AI Engine API",
        "version": settings.app_version,
        "docs": "/docs"
    }

@app.get("/health")
async def health() -> dict[str, str]:
	return {"status": "ok"}


@app.get("/adapter-test")
async def test_adapter() -> dict[str, Any]:
    from database.adapter.registry.registry import ConnectorRegistry
    # Test triggering the metadata sync!
    db_url = os.getenv("DATABASE_URL", "sqlite:///test.db")
    
    # Actually instantiate a connector and connect to trigger __aenter__ and sync_metadata
    async with ConnectorRegistry.create_connector(db_url, table_name="auth_user") as connector:
        # Just connecting triggers the metadata sync to Postgres!
        metadata = await connector.discover_metadata()

    return {
        "status": "success",
        "message": "Adapter successfully connected and metadata synced to Postgres!",
        "detected_metadata": metadata,
        "registered_connectors": list(ConnectorRegistry.list_connectors().keys()),
    }
