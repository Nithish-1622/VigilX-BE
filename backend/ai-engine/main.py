from __future__ import annotations
import socket
if not hasattr(socket, 'EAI_ADDRFAMILY'):
    socket.EAI_ADDRFAMILY = getattr(socket, 'EAI_FAMILY', 2)
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

from routers.ask import router as ask_router
from routers.voice import router as voice_router
from routers.history import router as history_router
from routers.documents import router as documents_router
from routers.graph import router as graph_router
from routers.profiling import router as profiling_router
app.include_router(ask_router)
app.include_router(voice_router)
app.include_router(history_router)
app.include_router(documents_router)
app.include_router(graph_router)
app.include_router(profiling_router)


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
    return {
        "status": "success",
        "registered_connectors": list(ConnectorRegistry.list_connectors().keys()),
        "test_detections": {
            "postgres://user:pass@localhost/db": SourceDetector.detect_source_type("postgres://user:pass@localhost/db"),
            "data.pdf": SourceDetector.detect_source_type("data.pdf"),
            "data.csv": SourceDetector.detect_source_type("data.csv"),
            "mongodb://localhost:27017": SourceDetector.detect_source_type("mongodb://localhost:27017")
        }
    }
