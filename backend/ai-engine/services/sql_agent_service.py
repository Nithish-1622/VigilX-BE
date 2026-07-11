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

        response: RestInvocationResponse = self._rest_gateway.invoke(
            structured_query,
            auth_header=auth_header,
            context_headers=context_headers,
        )
        rows = []
        if response.success:
            rows = response.payload.get("items", []) if isinstance(response.payload, dict) else []
        return SQLAgentResult(plan=structured_query.model_dump_json(), records=rows)
