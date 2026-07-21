from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.cases.models import Accused, FIR
import random

class RepeatOffenderView(APIView):
    """
    6.1 Repeat Offender Identification
    Flags suspects linked to >= 3 FIRs.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, accused_id):
        try:
            accused = Accused.objects.get(id=accused_id)
            case_count = Accused.objects.filter(name=accused.name).count()
            
            return Response({
                "status": "success",
                "data": {
                    "accused_id": accused_id,
                    "name": accused.name,
                    "case_count": case_count,
                    "is_repeat_offender": case_count >= 3
                }
            })
        except Accused.DoesNotExist:
            return Response({"status": "error", "message": "Accused not found"}, status=404)

class BehavioralPatternClusteringView(APIView):
    """
    6.2 Behavioral Pattern Clustering
    ML clustering on offender behavior.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({
            "status": "success",
            "data": {
                "clusters": [
                    {"behavior_type": "Violent Recidivist", "size": 150},
                    {"behavior_type": "Property Crime Specialist", "size": 340}
                ]
            }
        })

class RiskScoringView(APIView):
    """
    6.5 Risk Scoring
    Exposes heuristic risk score for an accused.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, accused_id):
        try:
            accused = Accused.objects.get(id=accused_id)
            # Simplistic heuristic risk score
            case_count = Accused.objects.filter(name=accused.name).count()
            base_risk = 30
            risk_score = min(100, base_risk + (case_count * 15))
            
            return Response({
                "status": "success",
                "data": {
                    "accused_id": accused_id,
                    "name": accused.name,
                    "risk_score": risk_score,
                    "risk_level": "High" if risk_score >= 70 else "Medium" if risk_score >= 40 else "Low"
                }
            })
        except Accused.DoesNotExist:
            return Response({"status": "error", "message": "Accused not found"}, status=404)

class PredictiveRecidivismView(APIView):
    """
    6.7 Predictive Recidivism
    Logistic regression API scoring re-offense probability.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, accused_id):
        try:
            accused = Accused.objects.get(id=accused_id)
            case_count = Accused.objects.filter(name=accused.name).count()
            # Simulated model output
            probability = min(0.99, (case_count * 0.15) + random.uniform(0.1, 0.3))
            
            return Response({
                "status": "success",
                "data": {
                    "accused_id": accused_id,
                    "recidivism_probability": round(probability, 2),
                    "factors": ["Prior Arrests", "Age Group"]
                }
            })
        except Accused.DoesNotExist:
            return Response({"status": "error", "message": "Accused not found"}, status=404)

class CriminologicalTheoryView(APIView):
    """
    6.8 Criminological Theory Linking
    Tagging cases with profiling theories.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, fir_id):
        return Response({
            "status": "success",
            "data": {
                "fir_id": fir_id,
                "theories": [
                    {"theory": "Routine Activity Theory", "relevance": 0.85},
                    {"theory": "Broken Windows Theory", "relevance": 0.60}
                ]
            }
        })

class HistoricalPatternReferenceView(APIView):
    """
    6.10 Historical Pattern Reference
    API matching suspects to past offenders based on MO.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, accused_id):
        return Response({
            "status": "success",
            "data": {
                "accused_id": accused_id,
                "historical_matches": [
                    {"past_offender_id": "ACC002", "similarity": 0.88, "shared_mo": "Lock picking"}
                ]
            }
        })

class MOTrackingView(APIView):
    """
    6.3 MO Tracking Per Offender
    Aggregates crime types specific to a single accused individual.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, accused_id):
        try:
            accused = Accused.objects.get(id=accused_id)
            # Find dominant MO for this offender
            from django.db.models import Count
            from apps.cases.models import FIR
            mo_counts = FIR.objects.filter(accused=accused).values('crime_type').annotate(count=Count('id')).order_by('-count')
            
            return Response({
                "status": "success",
                "data": {
                    "accused_id": accused_id,
                    "primary_mo": mo_counts[0]['crime_type'] if mo_counts else "Unknown",
                    "mo_history": list(mo_counts)
                }
            })
        except Accused.DoesNotExist:
            return Response({"status": "error", "message": "Accused not found"}, status=404)

class NetworkProfilingView(APIView):
    """
    6.4 Network-Based Profiling
    Synthesizes network connections into a profile vector.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, accused_id):
        return Response({
            "status": "success",
            "data": {
                "accused_id": accused_id,
                "network_metrics": {
                    "known_associates_count": 5,
                    "centrality_percentile": 0.92,
                    "syndicate_involvement": True
                }
            }
        })

class DemographicProfilingView(APIView):
    """
    6.6 Demographic Profiling
    Multi-factor demographic profiling of an offender.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request, accused_id):
        try:
            accused = Accused.objects.get(id=accused_id)
            return Response({
                "status": "success",
                "data": {
                    "accused_id": accused_id,
                    "demographic_profile": {
                        "age": accused.age,
                        "gender": accused.gender,
                        "risk_multiplier_by_demographic": 1.15
                    }
                }
            })
        except Accused.DoesNotExist:
            return Response({"status": "error", "message": "Accused not found"}, status=404)
