from __future__ import annotations

import shutil
import time
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/ml/telemetry", tags=["ML Telemetry"])


def _get_hardware_metrics() -> dict[str, Any]:
    """Collect current hardware metrics using psutil and torch (if available)."""
    metrics: dict[str, Any] = {
        "cpu_percent": 0.0,
        "ram_used_gb": 0.0,
        "ram_total_gb": 0.0,
        "ram_percent": 0.0,
        "gpu_available": False,
        "gpu_vram_used_mb": None,
        "gpu_vram_total_mb": None,
        "gpu_percent": None,
        "gpu_name": None,
        "timestamp": time.time(),
    }

    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        vm = psutil.virtual_memory()
        metrics["cpu_percent"] = cpu
        metrics["ram_used_gb"] = round(vm.used / (1024 ** 3), 2)
        metrics["ram_total_gb"] = round(vm.total / (1024 ** 3), 2)
        metrics["ram_percent"] = vm.percent
    except ImportError:
        pass

    try:
        import torch
        if torch.cuda.is_available():
            device = torch.device("cuda")
            metrics["gpu_available"] = True
            metrics["gpu_name"] = torch.cuda.get_device_name(0)
            metrics["gpu_vram_used_mb"] = round(
                torch.cuda.memory_allocated(0) / (1024 ** 2), 2
            )
            metrics["gpu_vram_total_mb"] = round(
                torch.cuda.get_device_properties(0).total_memory / (1024 ** 2), 2
            )
    except (ImportError, Exception):
        pass

    return metrics


@router.get("/hardware")
async def get_hardware_metrics(
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> JSONResponse:
    """
    GET /ml/telemetry/hardware
    Returns current GPU VRAM, GPU utilization, CPU%, and RAM usage.
    """
    try:
        metrics = _get_hardware_metrics()
        return JSONResponse(content={"status": "ok", "metrics": metrics})
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "detail": str(exc)},
        )


@router.get("/status")
async def get_service_status(
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> JSONResponse:
    """
    GET /ml/telemetry/status
    Returns overall ML Studio service health and availability.
    """
    from ml_studio.config import ml_settings
    from pathlib import Path

    registry_ok = Path(ml_settings.registry_dir).exists()

    ollama_reachable = False
    try:
        import httpx
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{ml_settings.ollama_base_url}/api/tags")
            ollama_reachable = resp.status_code == 200
    except Exception:
        pass

    return JSONResponse(content={
        "status": "ok",
        "registry_ready": registry_ok,
        "ollama_reachable": ollama_reachable,
        "hardware": _get_hardware_metrics(),
    })


@router.get("/job/{job_id}/live")
async def get_job_live(
    job_id: str,
    tenant_id: str = Header(default="default", alias="X-Tenant-ID"),
) -> JSONResponse:
    from datetime import datetime
    from ml_studio.core.model_registry import JobRegistry
    from ml_studio.config import ml_settings

    job = JobRegistry().get(job_id, tenant_id=tenant_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")

    hw = _get_hardware_metrics()
    usage = shutil.disk_usage(ml_settings.registry_dir)
    disk = {
        "total_gb": round(usage.total / (1024 ** 3), 2),
        "used_gb": round(usage.used / (1024 ** 3), 2),
        "free_gb": round(usage.free / (1024 ** 3), 2),
    }

    eta_seconds = None
    if job.started_at and job.progress and job.progress > 0 and job.progress < 100:
        elapsed = (datetime.utcnow() - job.started_at).total_seconds()
        eta_seconds = round(elapsed * ((100.0 / job.progress) - 1.0), 1)

    return JSONResponse(content={
        "job": {
            "job_id": job.job_id,
            "tenant_id": getattr(job, "tenant_id", "default") or "default",
            "job_name": job.job_name,
            "status": job.status.value,
            "progress": job.progress,
            "current_step": job.current_step,
            "total_steps": job.total_steps,
            "loss": job.loss,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None,
            "eta_seconds": eta_seconds,
        },
        "hardware": hw,
        "disk": disk,
        "timestamp": time.time(),
    })
