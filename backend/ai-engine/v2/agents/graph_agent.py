from __future__ import annotations

import os

from schemas.common import Citation
from v2.schemas.execution_plan import ToolCall, ToolType
from v2.schemas.tool_result import ToolResult
from v2.state import V2WorkflowState


class GraphIntelligenceAgent:
    """
    Agent 8: Graph Intelligence Agent
    Single responsibility: Neo4j criminal network traversals.

    Operations: network_overview | community_detection | centrality | hidden_links | shortest_path

    Reuses the Cypher query patterns from V1 routers/graph.py.
    No LLM. No REST calls. Direct Neo4j bolt connection.
    Falls back gracefully if Neo4j is unavailable.
    """

    async def handle(self, tool_call: ToolCall, state: V2WorkflowState) -> ToolResult:
        """Handler registered with ToolRouterAgent for ToolType.GRAPH."""
        params = tool_call.parameters or {}
        operation = params.get("operation", "network_overview")

        try:
            from neo4j import GraphDatabase  # type: ignore

            uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
            user = os.environ.get("NEO4J_USER", "neo4j")
            password = os.environ.get("NEO4J_PASSWORD", "")
            driver = GraphDatabase.driver(uri, auth=(user, password))

            records, text = self._execute(driver, operation, params, state)
            driver.close()

            citations = [
                Citation(
                    source="neo4j_graph",
                    snippet=str(r)[:200] if not isinstance(r, dict) else self._rec_snippet(r),
                )
                for r in records[:5]
            ]

            return ToolResult(
                tool=ToolType.GRAPH,
                subtask_id=tool_call.subtask_id,
                success=True,
                records=records,
                text=text,
                citations=citations,
                metadata={"operation": operation},
            )

        except ImportError:
            return ToolResult(
                tool=ToolType.GRAPH,
                success=False,
                error="neo4j package not installed",
            )
        except Exception as exc:
            return ToolResult(
                tool=ToolType.GRAPH,
                subtask_id=tool_call.subtask_id,
                success=False,
                error=f"Graph operation '{operation}' failed: {exc}",
            )

    def _execute(
        self,
        driver,
        operation: str,
        params: dict,
        state: V2WorkflowState,
    ) -> tuple[list[dict], str]:
        if operation == "community_detection":
            return self._community_detection(driver)
        if operation == "centrality":
            return self._centrality(driver)
        if operation == "hidden_links":
            return self._hidden_links(driver, params.get("suspect_id", ""))
        if operation == "shortest_path":
            return self._shortest_path(
                driver,
                params.get("source_id", ""),
                params.get("target_id", ""),
            )
        # Default: network overview for the given FIR or top-level graph
        return self._network_overview(driver, params.get("fir_id"))

    def _network_overview(self, driver, fir_id: str | None) -> tuple[list[dict], str]:
        with driver.session() as session:
            if fir_id:
                result = session.run(
                    "MATCH (c:Case {id: $fir_id})-[r]-(n) RETURN type(r) AS rel, labels(n) AS node_type, n LIMIT 40",
                    fir_id=fir_id,
                )
            else:
                result = session.run(
                    "MATCH (n)-[r]->(m) RETURN labels(n) AS src_type, type(r) AS rel, labels(m) AS tgt_type LIMIT 40"
                )
            records = [dict(r) for r in result]
        text = f"Graph overview: {len(records)} entity relationships found"
        return records, text

    def _community_detection(self, driver) -> tuple[list[dict], str]:
        with driver.session() as session:
            result = session.run("""
                MATCH (a1:Person {type: 'Accused'})-[:ACCUSED_IN]->(c:Case)<-[:ACCUSED_IN]-(a2:Person {type: 'Accused'})
                WHERE id(a1) < id(a2)
                RETURN a1.name AS accused_1, a2.name AS accused_2,
                       c.id AS shared_case, c.crime_type AS crime_type
                LIMIT 20
            """)
            records = [dict(r) for r in result]
        text = f"Community detection: {len(records)} co-accused pairs identified"
        return records, text

    def _centrality(self, driver) -> tuple[list[dict], str]:
        with driver.session() as session:
            result = session.run("""
                MATCH (a:Person {type: 'Accused'})-[r]-()
                RETURN a.id AS accused_id, a.name AS name, count(r) AS degree_centrality
                ORDER BY degree_centrality DESC LIMIT 10
            """)
            records = [dict(r) for r in result]
        top_names = ", ".join(
            f"{r.get('name', '?')}({r.get('degree_centrality', 0)})" for r in records[:3]
        )
        text = f"Centrality analysis — top suspects: {top_names}"
        return records, text

    def _hidden_links(self, driver, suspect_id: str) -> tuple[list[dict], str]:
        with driver.session() as session:
            result = session.run("""
                MATCH (a1:Person {type: 'Accused', id: $sid})-[:ACCUSED_IN]->(c1:Case)
                      <-[:ACCUSED_IN]-(a2:Person {type: 'Accused'})-[:ACCUSED_IN]->(c2:Case)
                      <-[:ACCUSED_IN]-(a3:Person {type: 'Accused'})
                WHERE a1 <> a3
                RETURN a3.name AS hidden_link, a3.id AS hidden_id,
                       count(c2) AS connection_strength
                ORDER BY connection_strength DESC LIMIT 5
            """, sid=suspect_id)
            records = [dict(r) for r in result]
        text = f"Hidden links for suspect {suspect_id}: {len(records)} indirect connections found"
        return records, text

    def _shortest_path(self, driver, source_id: str, target_id: str) -> tuple[list[dict], str]:
        with driver.session() as session:
            result = session.run(
                """
                MATCH p = shortestPath((s {id: $src})-[*..6]-(t {id: $tgt}))
                RETURN length(p) AS path_length, [n IN nodes(p) | coalesce(n.name, n.id, 'unknown')] AS path_nodes
                """,
                src=source_id,
                tgt=target_id,
            )
            records = [dict(r) for r in result]
        text = f"Shortest path {source_id}→{target_id}: {len(records)} path(s) found"
        return records, text

    @staticmethod
    def _rec_snippet(rec: dict) -> str:
        return "; ".join(f"{k}={v}" for k, v in list(rec.items())[:4] if v is not None)
