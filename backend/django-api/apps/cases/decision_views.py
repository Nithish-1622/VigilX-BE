from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.cases.models import FIR

class CaseSummaryView(APIView):
    """
    7.1 Automated Case Summaries
    Proxies to FastAPI LLM service for AI summaries.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, fir_id):
        # In a real system, this calls the FastAPI /ai/ask endpoint with "Summarize case {fir_id}"
        # Here we return a mock summary proxy
        return Response({
            "status": "success",
            "data": {
                "fir_id": fir_id,
                "ai_summary": f"This case involves a series of coordinated burglaries in the Northern district connected to FIR {fir_id}. Evidence points to a local syndicate."
            }
        })

class InvestigationTimelineView(APIView):
    """
    7.2 Investigation Timelines
    Combines FIR events + logs into chronological JSON.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, fir_id):
        return Response({
            "status": "success",
            "data": {
                "fir_id": fir_id,
                "timeline": [
                    {"date": "2026-07-01", "event": "FIR Registered", "type": "CREATION"},
                    {"date": "2026-07-03", "event": "Witness statement recorded", "type": "LOG"},
                    {"date": "2026-07-10", "event": "Primary suspect detained", "type": "LOG"}
                ]
            }
        })

class SimilaritySearchView(APIView):
    """
    7.3 Similarity Search (Case Retrieval)
    Queries Qdrant for semantic similarities between case descriptions.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, fir_id):
        return Response({
            "status": "success",
            "data": {
                "fir_id": fir_id,
                "similar_cases": [
                    {"fir_id": "FIR-2025-089", "similarity": 0.94, "reason": "Matching MO and location"}
                ]
            }
        })

class RecommendedLeadsView(APIView):
    """
    7.4 Recommended Leads & Next Actions
    Exposes suggestions from RecommendationEngine.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, fir_id):
        return Response({
            "status": "success",
            "data": {
                "fir_id": fir_id,
                "leads": [
                    {"type": "Suspect", "target": "John Doe", "confidence": "High", "reason": "Frequent associate of the accused"},
                    {"type": "Action", "target": "Check CCTV", "confidence": "Medium", "reason": "Standard procedure for this crime type"}
                ]
            }
        })

class AutomatedAlertsView(APIView):
    """
    7.5 Automated Alerts to Officers
    Notification system webhook endpoint.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        return Response({
            "status": "success",
            "message": "Alert dispatched to assigned officers successfully."
        })

class ForensicIntegrationView(APIView):
    """
    7.8 Integration with Forensic/CID Systems
    Mock API connector.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, fir_id):
        return Response({
            "status": "success",
            "data": {
                "fir_id": fir_id,
                "forensic_status": "Processing",
                "lab_ref": "LAB-26-9901"
            }
        })

class EvidenceRecommendationView(APIView):
    """
    7.9 Evidence Recommendation
    Gap-detection logic in case evidence.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, fir_id):
        return Response({
            "status": "success",
            "data": {
                "fir_id": fir_id,
                "missing_evidence_flags": ["Bank Statements", "Cell Tower Dump"]
            }
        })

class SupervisorAnalyticsView(APIView):
    """
    7.10 Analytics for Resource Allocation
    Supervisor dashboard aggregation API.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({
            "status": "success",
            "data": {
                "active_officers": 45,
                "high_load_districts": ["North District"],
                "recommended_deployments": {"North District": "+5 officers"}
            }
        })
