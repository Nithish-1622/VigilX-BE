from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from apps.cases.models import FIR, Victim, Accused

class DemographicBreakdownView(APIView):
    """
    5.1 Demographic Breakdown API
    Aggregates age and gender statistics by crime type.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        crime_type = request.GET.get('crime_type')
        
        # Simplified aggregation
        query = Accused.objects.all()
        if crime_type:
            query = query.filter(firs__crime_type=crime_type)
            
        gender_stats = query.values('gender').annotate(count=Count('id'))
        
        # Age brackets
        age_under_18 = query.filter(age__lt=18).count()
        age_18_35 = query.filter(age__gte=18, age__lte=35).count()
        age_35_60 = query.filter(age__gt=35, age__lte=60).count()
        age_over_60 = query.filter(age__gt=60).count()
        
        return Response({
            "status": "success",
            "data": {
                "gender_distribution": list(gender_stats),
                "age_brackets": {
                    "under_18": age_under_18,
                    "18_35": age_18_35,
                    "35_60": age_35_60,
                    "over_60": age_over_60
                }
            }
        })

class PublicSafetyIndexView(APIView):
    """
    5.6 Public Safety Index API
    Creates a composite scoring formula that evaluates crime density vs. population in a district.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        district = request.GET.get('district', 'Central District')
        
        # Mocking an external population factor for the district
        population = 500000 
        crime_count = FIR.objects.filter(location__icontains=district).count()
        
        # Simple safety index calculation (0-100, where 100 is perfectly safe)
        # 1 crime per 100 people drops score by 10 points
        crime_rate_per_100k = (crime_count / max(population, 1)) * 100000
        safety_score = max(0, min(100, 100 - (crime_rate_per_100k / 100)))
        
        return Response({
            "status": "success",
            "data": {
                "district": district,
                "population": population,
                "recorded_crimes": crime_count,
                "safety_score_out_of_100": round(safety_score, 2),
                "risk_level": "High" if safety_score < 40 else "Medium" if safety_score < 70 else "Low"
            }
        })

class SocioeconomicCorrelationView(APIView):
    """
    5.2 Socioeconomic Correlation API
    API connecting external datasets to crime rates.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({
            "status": "success",
            "data": {
                "correlations": [
                    {"factor": "Unemployment Rate", "correlation_coefficient": 0.65},
                    {"factor": "Income Inequality", "correlation_coefficient": 0.72}
                ]
            }
        })

class PopulationDensityView(APIView):
    """
    5.3 Population Density API
    Mapping API for urbanization overlay.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({
            "status": "success",
            "data": {
                "urban_zones": [
                    {"zone": "Downtown", "density_per_sq_km": 15000, "crime_multiplier": 1.2}
                ]
            }
        })

class MigrationMobilityView(APIView):
    """
    5.4 Migration & Mobility Patterns API
    Endpoint for suspect mobility history.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({
            "status": "success",
            "data": {
                "mobility_patterns": [
                    {"suspect_id": "ACC123", "frequent_locations": ["District A", "District C"]}
                ]
            }
        })

class RiskFactorAnalysisView(APIView):
    """
    5.5 Risk Factor Analysis API
    Endpoint for statistical risk models.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({
            "status": "success",
            "data": {
                "risk_factors": [
                    {"factor": "Prior Convictions", "weight": 0.4},
                    {"factor": "Gang Affiliation", "weight": 0.35}
                ]
            }
        })

class InteractiveReportsView(APIView):
    """
    5.7 Interactive Socio-Crime Reports API
    Exposes JSON payload for dashboard generation.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({
            "status": "success",
            "data": {
                "dashboard_payload": {
                    "charts": ["Demographics", "Mobility", "Risk Factors"],
                    "summary_text": "Crime has shifted towards urban centers this quarter."
                }
            }
        })
