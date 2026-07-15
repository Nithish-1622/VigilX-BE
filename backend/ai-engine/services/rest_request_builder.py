from __future__ import annotations

from schemas.rest import RestEndpointDefinition, RestInvocationRequest, StructuredQuery


class RestRequestBuilder:
    def build(
        self,
        definition: RestEndpointDefinition,
        query: StructuredQuery,
        auth_header: str | None = None,
        context_headers: dict[str, str] | None = None,
    ) -> RestInvocationRequest | None:
        if not definition.path:
            return None

        headers = dict(context_headers or {})
        if auth_header:
            headers["Authorization"] = auth_header

        return RestInvocationRequest(
            definition=definition,
            query=query,
            auth_header=auth_header,
            context_headers=headers,
        )
