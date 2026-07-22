from __future__ import annotations

from schemas.rest import RestCapability, RestInvocationRequest, RestInvocationResponse, StructuredQuery
from services.rest_client import RestClient
from services.rest_endpoint_registry import RestEndpointRegistry
from services.rest_request_builder import RestRequestBuilder
from services.rest_response_parser import RestResponseParser
from utils.config import settings


class DjangoRestGateway:
    def __init__(self) -> None:
        self._registry = RestEndpointRegistry()
        self._client = RestClient(registry=self._registry)
        self._builder = RestRequestBuilder()
        self._parser = RestResponseParser()

    def invoke(
        self,
        query: StructuredQuery,
        auth_header: str | None = None,
        context_headers: dict[str, str] | None = None,
    ) -> RestInvocationResponse:
        definition = self._registry.get(query.capability)
        if definition is None:
            return RestInvocationResponse(
                capability=query.capability,
                success=False,
                error=f"endpoint_not_configured:{query.capability.value}",
            )

        headers = context_headers.copy() if context_headers else {}
        if auth_header:
            headers["Authorization"] = auth_header

        invocation = self._builder.build(
            definition,
            query,
            auth_header=headers.get("Authorization"),
            context_headers=headers,
        )
        if invocation is None:
            return RestInvocationResponse(
                capability=query.capability,
                success=False,
                error=f"request_not_configured:{query.capability.value}",
            )

        response = self._client.invoke(invocation)
        if not response.success:
            return response

        items = self._parser.parse_items(definition, response.payload)
        return RestInvocationResponse(
            capability=query.capability,
            success=True,
            status_code=response.status_code,
            attempts=response.attempts,
            payload={"items": items},
        )
