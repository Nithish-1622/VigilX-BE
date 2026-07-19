from __future__ import annotations

import os
import unittest

from schemas.rest import RestCapability, RestEndpointDefinition, RestInvocationRequest, RestMethod, StructuredQuery
from services.rest_client import RestClient
from services.rest_endpoint_registry import RestEndpointRegistry
from services.rest_gateway import DjangoRestGateway
from services.rest_request_builder import RestRequestBuilder
from services.rest_response_parser import RestResponseParser


class RestGatewayTests(unittest.TestCase):
    def test_request_builder_returns_invocation_for_configured_definition(self) -> None:
        builder = RestRequestBuilder()
        definition = RestEndpointDefinition(
            capability=RestCapability.CASE_SEARCH,
            path="/cases/search",
            method=RestMethod.POST,
            request_body_key="payload",
        )
        query = StructuredQuery(capability=RestCapability.CASE_SEARCH, intent="case_lookup", question="q")

        invocation = builder.build(definition, query, auth_header="Bearer x", context_headers={"x-user-id": "u"})

        self.assertIsNotNone(invocation)
        self.assertEqual(invocation.definition.path, "/cases/search")
        self.assertEqual(invocation.context_headers["x-user-id"], "u")

    def test_response_parser_accepts_generic_items(self) -> None:
        parser = RestResponseParser()
        definition = RestEndpointDefinition(capability=RestCapability.CRIME_RECORDS, path="/records")
        payload = {"data": {"items": [{"id": 1, "name": "A"}]}}

        items = parser.parse_items(definition, payload)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], "A")

    def test_gateway_returns_not_configured_when_base_url_missing(self) -> None:
        from unittest.mock import patch
        with patch.object(RestEndpointRegistry, "get", return_value=None):
            gateway = DjangoRestGateway()
            query = StructuredQuery(capability=RestCapability.CASE_SEARCH, intent="case_lookup", question="q")
        
            response = gateway.invoke(query)
        
            self.assertFalse(response.success)
            self.assertIn("endpoint_not_configured", response.error or "")


if __name__ == "__main__":
    unittest.main()