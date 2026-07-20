from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, status, BackgroundTasks
import httpx

from agents.workflow import AIOrchestrator
from schemas.common import ErrorDetail, StandardResponse
from schemas.conversation import AskRequest
from utils.logging import get_logger
from utils.config import settings

logger = get_logger(__name__)
router = APIRouter(prefix="/ai", tags=["ai-engine"])
orchestrator = AIOrchestrator()

async def log_audit_to_django(req: AskRequest, auth_header: str | None, response_intent: str):
    if not auth_header: return
    try:
        url = f"{settings.rest_base_url.replace('/api', '')}/api/audit/"
        payload = {
            "action": f"AI_QUERY_{response_intent.upper()}",
            "entity_name": "AI_ENGINE",
            "entity_id": req.session_id,
            "details": {"question": req.question}
        }
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload, headers={"Authorization": auth_header})
    except Exception as e:
        logger.warning(f"Failed to log audit to Django: {e}")

@router.post(
    "/ask",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
)
async def ask(
    req: AskRequest,
    background_tasks: BackgroundTasks,
    authorization: str | None = Header(default=None),
) -> StandardResponse:
    try:
        res = await orchestrator.run(req, auth_header=authorization)
        background_tasks.add_task(log_audit_to_django, req, authorization, res.metadata.intent)
        return res
    except ValueError as exc:
        logger.warning("Validation-like workflow error: %s", exc)
        return StandardResponse(
            success=False,
            message="request failed",
            data={},
            metadata={},
            citations=[],
            errors=[ErrorDetail(code="bad_request", message=str(exc))],
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Unhandled AI workflow failure")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "internal error",
                "data": {},
                "metadata": {},
                "citations": [],
                "errors": [{"code": "internal_error", "message": str(exc)}],
            },
        ) from exc

@router.post("/feedback")
async def ai_feedback(query_id: str, rating: int, comments: str = ""):
    """
    10.8 Feedback Loop
    Endpoint to rate AI answers.
    """
    try:
        logger.info(f"Feedback for query {query_id}: {rating}/5 - {comments}")
        return StandardResponse(
            success=True,
            message="Feedback received successfully",
            data={"query_id": query_id, "rating": rating},
            metadata=None,
            citations=[],
            errors=[]
        )
    except Exception as e:
        logger.error(f"Error logging feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))
