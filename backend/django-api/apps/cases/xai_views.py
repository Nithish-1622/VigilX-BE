from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class ReasoningVisualizationView(APIView):
    """
    10.2 Reasoning Visualization
    Returns subgraph highlighting data for UI.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, query_id):
        return Response({
            "status": "success",
            "data": {
                "query_id": query_id,
                "reasoning_path": ["Extracted Intent: Gang Match", "Queried Neo4j for shortest path", "Found connection via BankAccount"],
                "subgraph_nodes": ["ACC-10", "TX-990", "ACC-44"]
            }
        })

class ModelTransparencyView(APIView):
    """
    10.6 Model Transparency Controls
    API to inspect LLM version or prompt configs.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({
            "status": "success",
            "data": {
                "active_model": "llama-3.1-8b-instruct",
                "temperature": 0.2,
                "vector_db": "Qdrant",
                "graph_db": "Neo4j version 5.12"
            }
        })

class ExplainableRiskView(APIView):
    """
    10.7 Explainable ML Models
    Explains the risk score formula.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, accused_id):
        return Response({
            "status": "success",
            "data": {
                "accused_id": accused_id,
                "base_score": 30,
                "contributing_factors": [
                    {"factor": "Prior Convictions (x3)", "impact": "+45"},
                    {"factor": "Demographic Multiplier", "impact": "* 1.15"}
                ],
                "final_score": 86.25,
                "decision_tree_path": "High Recidivist Branch"
            }
        })

class EthicalGuardrailsView(APIView):
    """
    10.9 Ethical Guardrails
    Bias-detection and fairness checks config.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({
            "status": "success",
            "data": {
                "guardrails_active": True,
                "filtered_attributes": ["race", "religion"],
                "bias_score": 0.02,
                "status": "Pass"
            }
        })
