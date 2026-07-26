from __future__ import annotations

# pyrefly: ignore [missing-import]
import httpx
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, status

from schemas.conversation import AskRequest
from utils.config import settings
from utils.logging import get_logger
from v2.orchestrator import V2AIOrchestrator
from v2.schemas.investigation_response import InvestigationResponse

logger = get_logger(__name__)

router = APIRouter(prefix="/ai/v2", tags=["ai-engine-v2"])

# Singleton orchestrator — initialised once on startup
_orchestrator: V2AIOrchestrator | None = None


def get_orchestrator() -> V2AIOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = V2AIOrchestrator()
    return _orchestrator


@router.post(
    "/ask",
    response_model=InvestigationResponse,
    status_code=status.HTTP_200_OK,
    summary="V2 Multi-Agent Investigation Query",
    description=(
        "20-agent investigation intelligence pipeline. "
        "Returns structured InvestigationResponse with evidence bundle, "
        "key findings, timeline, entity relationships, citations, "
        "chart specifications, and investigation recommendations. "
        "LLM is invoked only after evidence verification gate."
    ),
)
async def ask_v2(
    req: AskRequest,
    background_tasks: BackgroundTasks,
    authorization: str | None = Header(default=None),
) -> InvestigationResponse:
    try:
        orchestrator = get_orchestrator()
        response = await orchestrator.run(req, auth_header=authorization)

        # Audit log in background — does not block response
        background_tasks.add_task(
            _audit_log,
            req=req,
            auth_header=authorization,
            intent=response.intent,
            confidence=response.confidence_label,
            critic_passed=response.critic_passed,
        )
        return response

    except Exception as exc:
        logger.exception("V2 orchestration failure | session=%s", req.session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "V2 pipeline error",
                "detail": str(exc),
                "v2": True,
            },
        ) from exc


@router.get(
    "/registry",
    summary="List registered tool capabilities",
    description="Returns all tools registered in the ToolCapabilityRegistry with their descriptors.",
)
async def list_tools():
    from v2.registry.tool_registry import tool_registry
    enabled = tool_registry.all_enabled()
    return {
        "total": len(enabled),
        "core_tools": len([t for t in enabled if not t.is_optional]),
        "optional_tools": len([t for t in enabled if t.is_optional]),
        "tools": [cap.model_dump() for cap in enabled],
    }


@router.get("/health", summary="V2 engine health check")
async def health_v2():
    return {
        "status": "ok",
        "version": "v2",
        "agents": 20,
        "pipeline": "multi_agent_langgraph",
    }


# ── Background audit logger ───────────────────────────────────────────────────

async def _audit_log(
    req: AskRequest,
    auth_header: str | None,
    intent: str,
    confidence: str,
    critic_passed: bool,
) -> None:
    if not auth_header or not settings.rest_api_base_url:
        return
    try:
        base = settings.rest_api_base_url.rstrip("/")
        url = f"{base.replace('/api', '')}/api/audit/"
        payload = {
            "action": f"V2_AI_{intent.upper()}",
            "entity_name": "V2_AI_ENGINE",
            "entity_id": req.session_id,
            "details": {
                "question_length": len(req.question),
                "confidence": confidence,
                "critic_passed": critic_passed,
            },
        }
        async with httpx.AsyncClient(timeout=3.0) as client:
            await client.post(
                url,
                json=payload,
                headers={"Authorization": auth_header},
            )
    except Exception as exc:
        logger.debug("V2 audit log failed (non-critical): %s", exc)
