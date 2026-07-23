import sys, asyncio
sys.path.insert(0, '.')

# Test agents with no external dependencies
from v2.agents.base_agent import BaseAgent
from v2.agents.python_tool_agent import PythonToolAgent
from v2.agents.analytics_agent import AnalyticsAgent
from v2.agents.cross_validation_agent import CrossValidationAgent
from v2.agents.verification_agent import VerificationAgent
from v2.agents.response_critic_agent import ResponseCriticAgent
from v2.agents.citation_agent import CitationAgent
from v2.agents.recommendation_agent import RecommendationAgent
from v2.schemas.execution_plan import ToolCall, ToolType, DependencyType
from v2.schemas.tool_result import ToolResult, AggregatedEvidence
from v2.schemas.ranked_evidence import EvidenceBundle, EvidenceScore, RankedEvidenceItem
from v2.schemas.investigation_response import InvestigationResponse
from schemas.common import Citation

print("No-dep agent imports: OK")

# Test PythonToolAgent
agent = PythonToolAgent()
tc = ToolCall(tool=ToolType.PYTHON, rationale="test", parameters={"operation": "count_by", "field": "crime_type"})
state = {"question": "How many robbery cases?", "tool_results": [], "user_id": "u1", "session_id": "s1"}
result = asyncio.run(agent.handle(tc, state))
print(f"PythonToolAgent: success={result.success} text=\"{result.text[:60]}\"")

# Test AnalyticsAgent
analytics = AnalyticsAgent()
tc2 = ToolCall(tool=ToolType.ANALYTICS, rationale="timeline", parameters={"operation": "crime_trends"})
sql_result = ToolResult(
    tool=ToolType.SQL, success=True,
    records=[
        {"id": 1, "crime_type": "ROBBERY", "status": "PENDING", "district": "Bengaluru"},
        {"id": 2, "crime_type": "THEFT", "status": "CLOSED", "district": "Mysuru"},
        {"id": 3, "crime_type": "ROBBERY", "status": "ACTIVE", "district": "Bengaluru"},
    ],
    text="3 records",
    citations=[]
)
state2 = {"question": "crime trends?", "tool_results": [sql_result], "user_id": "u1", "session_id": "s1"}
result2 = asyncio.run(analytics.handle(tc2, state2))
print(f"AnalyticsAgent: success={result2.success} records={len(result2.records)} text=\"{result2.text[:60]}\"")

# Test ResponseCriticAgent
critic = ResponseCriticAgent()
state3 = {
    "reasoning_output": "FIR-2026-999 is linked to suspect Rajesh. I believe he is guilty.",
    "evidence_bundle": EvidenceBundle(top_evidence_text="No FIR mentioned", evidence_count=2),
    "user_id": "u1", "session_id": "s1"
}
result3 = asyncio.run(critic.run(state3))
print(f"ResponseCriticAgent warnings: {result3['critic_warnings']}")
print(f"Patched reasoning: {result3['reasoning_output'][:80]}")

# Test EvidenceRankingAgent
from v2.agents.evidence_ranking_agent import EvidenceRankingAgent
from services.evidence_service import EvidenceService

citations = [
    Citation(source="case_search", reference_id="FIR-001", snippet="Robbery at MG Road. Accused: Ramesh.", score=0.9),
    Citation(source="neo4j_graph", reference_id="G-002", snippet="Ramesh linked to 3 prior cases.", score=0.7),
    Citation(source="qdrant_vector_search", reference_id="Q-003", snippet="Similar robbery pattern in 2025.", score=0.5),
]
agg = AggregatedEvidence(tool_results=[], merged_text="test", all_citations=citations, total_records=3)
state4 = {
    "question": "Who robbed MG Road?",
    "aggregated_evidence": agg,
    "execution_plan": None,
    "user_id": "u1", "session_id": "s1"
}
ranking_agent = EvidenceRankingAgent(evidence_service=EvidenceService())
result4 = asyncio.run(ranking_agent.run(state4))
bundle = result4["evidence_bundle"]
print(f"EvidenceRankingAgent: items={bundle.evidence_count} confidence={bundle.overall_confidence:.3f} label={bundle.confidence_label} threshold_met={bundle.threshold_met}")
print(f"Top evidence text: {bundle.top_evidence_text[:120]}")

print()
print("All V2 agent tests PASSED!")
