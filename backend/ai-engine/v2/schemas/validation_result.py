from __future__ import annotations

from pydantic import BaseModel, Field


class Inconsistency(BaseModel):
    """A single data conflict detected between two sources."""

    field: str
    value_from_sql: str | None = None
    value_from_graph: str | None = None
    value_from_rag: str | None = None
    severity: str = "warning"            # warning | error


class CrossCheckReport(BaseModel):
    """
    Output of CrossValidationAgent.
    Logs conflicts between SQL, Graph, and RAG outputs for the same entities.
    Warnings do NOT block LLM reasoning. Errors do.
    """

    checked: bool = False
    inconsistencies: list[Inconsistency] = Field(default_factory=list)
    sql_graph_agreement: bool = True
    sql_rag_agreement: bool = True
    overall_consistent: bool = True      # False only if error-severity conflicts exist
    validation_notes: str = ""
