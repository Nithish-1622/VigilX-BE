from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.cases.models import BankAccount, Transaction, Accused

class TransactionNetworkView(APIView):
    """
    8.1 Transaction Network Graphs & 8.6 Visualization
    Exports financial flow for D3.js visualization.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, account_number):
        return Response({
            "status": "success",
            "data": {
                "nodes": [
                    {"id": account_number, "type": "BankAccount"},
                    {"id": "EXT-9001", "type": "BankAccount"}
                ],
                "links": [
                    {"source": account_number, "target": "EXT-9001", "amount": 15000, "suspicious": True}
                ]
            }
        })

class SuspiciousTransactionView(APIView):
    """
    8.2 Suspicious Transaction Detection
    Rule engine for AML tracking.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({
            "status": "success",
            "data": {
                "flagged_transactions": [
                    {"txn_id": "TX-001", "amount": 150000.00, "flag": "Exceeds $10k Threshold"},
                    {"txn_id": "TX-008", "amount": 4900.00, "flag": "High Velocity Structuring (Smurfing)"}
                ]
            }
        })

class FinancialEntityLinkView(APIView):
    """
    8.3 Linking Financial and Criminal Entities
    API mapping bank accounts to Accused.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, accused_id):
        return Response({
            "status": "success",
            "data": {
                "accused_id": accused_id,
                "linked_accounts": ["AC-778-999-1", "AC-000-444-2"]
            }
        })

class AMLWorkflowView(APIView):
    """
    8.4 Integrated AML Workflows
    Mock connector to external AML systems.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, txn_id):
        return Response({
            "status": "success",
            "message": f"Transaction {txn_id} successfully reported to FIU AML system."
        })

    def get(self, request, txn_id):
        return self.post(request, txn_id)

class CrossBorderTracingView(APIView):
    """
    8.5 Cross-Border Tracing
    Mock international database tracing.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, account_number):
        return Response({
            "status": "success",
            "data": {
                "jurisdiction": "Cayman Islands",
                "international_wire_count": 3,
                "total_exported_funds": 450000.00
            }
        })

class FinanceReportView(APIView):
    """
    8.7 Case-Centric Finance Reports
    Triggers generation of a financial intelligence PDF.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, fir_id):
        return Response({
            "status": "success",
            "message": f"Financial intelligence report for case {fir_id} generated.",
            "download_url": f"/media/reports/finance_{fir_id}.pdf"
        })

class FraudPatternMatchingView(APIView):
    """
    8.8 Pattern Matching (Fraud Detection)
    Mock ML pattern extraction on transaction histories.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({
            "status": "success",
            "data": {
                "identified_fraud_patterns": [
                    {"pattern": "Round-Tripping", "confidence": 0.88, "affected_accounts": 4}
                ]
            }
        })
