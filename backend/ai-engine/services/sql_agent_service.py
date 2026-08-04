from __future__ import annotations

from dataclasses import dataclass

from schemas.rest import RestInvocationResponse, StructuredQuery
from services.rest_gateway import DjangoRestGateway


@dataclass
class SQLAgentResult:
    plan: str
    records: list[dict]


class SQLAgentService:
    """
    Uses a REST-first contract and never executes SQL directly.
    """

    def __init__(self, rest_gateway: DjangoRestGateway) -> None:
        self._rest_gateway = rest_gateway

    async def execute_plan(
        self,
        structured_query: StructuredQuery | None,
        auth_header: str | None = None,
        context_headers: dict[str, str] | None = None,
    ) -> SQLAgentResult:
        if structured_query is None:
            return SQLAgentResult(plan="no_query", records=[])

        import asyncio
        response: RestInvocationResponse = await asyncio.to_thread(
            self._rest_gateway.invoke,
            structured_query,
            auth_header,
            context_headers,
        )
        rows = []
        if response.success and isinstance(response.payload, dict):
            # Django REST Framework pagination uses 'results', legacy/other might use 'items'
            rows = response.payload.get("results", response.payload.get("items", []))
        return SQLAgentResult(plan=structured_query.model_dump_json(), records=rows)
