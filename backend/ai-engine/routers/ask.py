from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, status

from agents.workflow import AIOrchestrator
from schemas.common import ErrorDetail, StandardResponse
from schemas.conversation import AskRequest
from utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/ai", tags=["ai-engine"])
orchestrator = AIOrchestrator()


@router.post(
    "/ask",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
)
async def ask(
    req: AskRequest,
    authorization: str | None = Header(default=None),
) -> StandardResponse:
    try:
        return await orchestrator.run(req, auth_header=authorization)
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
