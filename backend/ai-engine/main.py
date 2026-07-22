from __future__ import annotations
from typing import Any

from contextlib import asynccontextmanager

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

from database.adapter.registry.registry import ConnectorRegistry
from database.adapter.registry.detector import SourceDetector


@asynccontextmanager
async def lifespan(_: FastAPI):
	logger.info("Starting %s v%s", settings.app_name, settings.app_version)
	yield
	logger.info("Stopping %s", settings.app_name)


from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
	title=settings.app_name,
	version=settings.app_version,
	lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ask_router)


@app.get("/health")
async def health() -> dict[str, str]:
	return {"status": "ok"}


@app.get("/adapter-test")
async def test_adapter() -> dict[str, Any]:
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
