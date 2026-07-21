from __future__ import annotations
import socket
if not hasattr(socket, 'EAI_ADDRFAMILY'):
    socket.EAI_ADDRFAMILY = getattr(socket, 'EAI_FAMILY', 2)

from contextlib import asynccontextmanager

from fastapi import FastAPI

from routers.ask import router as ask_router
from utils.config import settings
from utils.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
	logger.info("Starting %s v%s", settings.app_name, settings.app_version)
	yield
	logger.info("Stopping %s", settings.app_name)


app = FastAPI(
	title=settings.app_name,
	version=settings.app_version,
	lifespan=lifespan,
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
