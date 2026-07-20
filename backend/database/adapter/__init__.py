"""
Universal Database Adapter
==========================

A production-ready, enterprise-grade adapter that enables seamless data 
retrieval, search, and understanding from any structured, semi-structured, 
or unstructured data source.

Example:
    from adapter import QueryPlanner, SearchQuery
    
    planner = QueryPlanner()
    query = SearchQuery(query_text="Find all suspicious transactions", hybrid=True)
    
    results = await planner.query_source("postgres://user:pass@localhost:5432/db", query)
"""

from .core.models import Record, SearchQuery
from .core.exceptions import AdapterException
from .query.planner import QueryPlanner
from .registry.registry import ConnectorRegistry

# Import connectors to trigger auto-registration
from .connectors import (
    postgres_connector, csv_connector, pdf_connector,
    mongodb_connector, neo4j_connector, excel_connector,
    json_connector, txt_connector, yaml_connector,
    api_connector, sqlite_connector, mysql_connector
)

# Expose primary API
__all__ = [
    "Record",
    "SearchQuery",
    "QueryPlanner",
    "ConnectorRegistry",
    "AdapterException"
]
