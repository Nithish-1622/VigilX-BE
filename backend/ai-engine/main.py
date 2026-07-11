from __future__ import annotations

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

app.include_router(ask_router)


@app.get("/health")
async def health() -> dict[str, str]:
	return {"status": "ok"}
