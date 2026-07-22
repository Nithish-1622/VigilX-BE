from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.users.views import UserViewSet
from apps.cases.views import FIRViewSet, VictimViewSet, AccusedViewSet, ClueEntityViewSet
from apps.investigation.views import InvestigationLogViewSet
from apps.audit.views import AuditLogViewSet
from apps.authentication.views import LoginView, RefreshView, LogoutView
from apps.reports.views import CaseReportView

# Central REST Router for VigilX models
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'cases', FIRViewSet, basename='cases')
router.register(r'victims', VictimViewSet, basename='victims')
router.register(r'accused', AccusedViewSet, basename='accused')
router.register(r'entities', ClueEntityViewSet, basename='entities')
router.register(r'investigations', InvestigationLogViewSet, basename='investigations')
router.register(r'audit', AuditLogViewSet, basename='audit')

from apps.cases.analytics_views import AutoSuggestView, EntityResolutionView, CaseFolderView, BulkUploadView
from apps.cases.trend_views import SpatioTemporalTrendView, ModusOperandiAnalyticsView, SeasonalAnalyticsView, ComparativeDashboardView, AnomalyDetectionView, GISIntegrationView, PatternMiningView
from apps.cases.socio_views import DemographicBreakdownView, SocioeconomicCorrelationView, PopulationDensityView, MigrationMobilityView, RiskFactorAnalysisView, PublicSafetyIndexView, InteractiveReportsView
from apps.cases.profiling_views import RepeatOffenderView, BehavioralPatternClusteringView, RiskScoringView, PredictiveRecidivismView, CriminologicalTheoryView, HistoricalPatternReferenceView, MOTrackingView, NetworkProfilingView, DemographicProfilingView
from apps.cases.decision_views import CaseSummaryView, InvestigationTimelineView, SimilaritySearchView, RecommendedLeadsView, AutomatedAlertsView, ForensicIntegrationView, EvidenceRecommendationView, SupervisorAnalyticsView
from apps.cases.finance_views import TransactionNetworkView, SuspiciousTransactionView, FinancialEntityLinkView, AMLWorkflowView, CrossBorderTracingView, FinanceReportView, FraudPatternMatchingView
from apps.cases.forecasting_views import HotspotPredictionView, GangActivityAlertsView, TrendExtrapolationView, EarlyWarningNotificationsView, PredictiveStaffingView, ModelRetrainingView, EventDrivenForecastingView, ReOffenderAlertsView
from apps.cases.xai_views import ReasoningVisualizationView, ModelTransparencyView, ExplainableRiskView, EthicalGuardrailsView

urlpatterns = [
    # Phase 2 Management APIs (Must be before router to avoid being caught as PK)
    path('cases/bulk-upload/', BulkUploadView.as_view(), name='api_bulk_upload'),
    path('cases/<str:fir_id>/folder/', CaseFolderView.as_view(), name='api_case_folder'),

    # Include default router URLs
    path('', include(router.urls)),

    # Analytics / Suggest API
    path('suggest/', AutoSuggestView.as_view(), name='api_autosuggest'),
    path('analytics/entity-resolution/', EntityResolutionView.as_view(), name='api_entity_resolution'),
    
    # Phase 4 Analytics APIs
    path('analytics/trends/', SpatioTemporalTrendView.as_view(), name='api_trends'),
    path('analytics/seasonal/', SeasonalAnalyticsView.as_view(), name='api_seasonal'),
    path('analytics/mo/', ModusOperandiAnalyticsView.as_view(), name='api_mo_analytics'),
    path('analytics/compare/', ComparativeDashboardView.as_view(), name='api_compare'),
    path('analytics/anomalies/', AnomalyDetectionView.as_view(), name='api_anomalies'),
    path('analytics/gis/', GISIntegrationView.as_view(), name='api_gis'),
    path('analytics/patterns/', PatternMiningView.as_view(), name='api_patterns'),

    # Phase 5 Socio-Demographic APIs
    path('analytics/demographics/', DemographicBreakdownView.as_view(), name='api_demographics'),
    path('analytics/socioeconomic/', SocioeconomicCorrelationView.as_view(), name='api_socioeconomic'),
    path('analytics/population-density/', PopulationDensityView.as_view(), name='api_population_density'),
    path('analytics/mobility/', MigrationMobilityView.as_view(), name='api_mobility'),
    path('analytics/risk-factors/', RiskFactorAnalysisView.as_view(), name='api_risk_factors'),
    path('analytics/safety-index/', PublicSafetyIndexView.as_view(), name='api_safety_index'),
    path('analytics/socio-reports/', InteractiveReportsView.as_view(), name='api_socio_reports'),

    # Phase 6 Profiling APIs
    path('profiling/repeat-offenders/<str:accused_id>/', RepeatOffenderView.as_view(), name='api_repeat_offender'),
    path('profiling/behavioral-clusters/', BehavioralPatternClusteringView.as_view(), name='api_behavioral_clusters'),
    path('profiling/risk-score/<str:accused_id>/', RiskScoringView.as_view(), name='api_risk_score'),
    path('profiling/recidivism/<str:accused_id>/', PredictiveRecidivismView.as_view(), name='api_predictive_recidivism'),
    path('profiling/theory/<str:fir_id>/', CriminologicalTheoryView.as_view(), name='api_criminological_theory'),
    path('profiling/historical-matches/<str:accused_id>/', HistoricalPatternReferenceView.as_view(), name='api_historical_matches'),
    path('profiling/mo-tracking/<str:accused_id>/', MOTrackingView.as_view(), name='api_mo_tracking'),
    path('profiling/network/<str:accused_id>/', NetworkProfilingView.as_view(), name='api_network_profiling'),
    path('profiling/demographics/<str:accused_id>/', DemographicProfilingView.as_view(), name='api_demographic_profiling'),

    # Phase 7 Investigator Decision Support APIs
    path('cases/<str:fir_id>/ai-summary/', CaseSummaryView.as_view(), name='api_case_summary'),
    path('cases/<str:fir_id>/timeline/', InvestigationTimelineView.as_view(), name='api_investigation_timeline'),
    path('cases/<str:fir_id>/similar/', SimilaritySearchView.as_view(), name='api_similarity_search'),
    path('cases/<str:fir_id>/leads/', RecommendedLeadsView.as_view(), name='api_recommended_leads'),
    path('cases/<str:fir_id>/forensics/', ForensicIntegrationView.as_view(), name='api_forensic_integration'),
    path('cases/<str:fir_id>/evidence-gaps/', EvidenceRecommendationView.as_view(), name='api_evidence_gaps'),
    path('alerts/dispatch/', AutomatedAlertsView.as_view(), name='api_automated_alerts'),
    path('supervisor/analytics/', SupervisorAnalyticsView.as_view(), name='api_supervisor_analytics'),

    # Phase 8 Financial Crime APIs
    path('finance/network/<str:account_number>/', TransactionNetworkView.as_view(), name='api_transaction_network'),
    path('finance/suspicious/', SuspiciousTransactionView.as_view(), name='api_suspicious_tx'),
    path('finance/entity-link/<str:accused_id>/', FinancialEntityLinkView.as_view(), name='api_finance_entity_link'),
    path('finance/aml/report/<str:txn_id>/', AMLWorkflowView.as_view(), name='api_aml_report'),
    path('finance/cross-border/<str:account_number>/', CrossBorderTracingView.as_view(), name='api_cross_border'),
    path('finance/report/<str:fir_id>/', FinanceReportView.as_view(), name='api_finance_report'),
    path('finance/fraud-patterns/', FraudPatternMatchingView.as_view(), name='api_fraud_patterns'),

    # Phase 9 Forecasting APIs
    path('forecasting/hotspots/', HotspotPredictionView.as_view(), name='api_hotspot_prediction'),
    path('forecasting/gang-alerts/', GangActivityAlertsView.as_view(), name='api_gang_alerts'),
    path('forecasting/trends/', TrendExtrapolationView.as_view(), name='api_trend_extrapolation'),
    path('forecasting/warnings/', EarlyWarningNotificationsView.as_view(), name='api_early_warnings'),
    path('forecasting/staffing/', PredictiveStaffingView.as_view(), name='api_predictive_staffing'),
    path('forecasting/retrain/', ModelRetrainingView.as_view(), name='api_model_retraining'),
    path('forecasting/events/', EventDrivenForecastingView.as_view(), name='api_event_forecasting'),
    path('forecasting/re-offender-alerts/', ReOffenderAlertsView.as_view(), name='api_reoffender_alerts'),

    # Phase 10 Explainable AI APIs
    path('xai/reasoning/<str:query_id>/', ReasoningVisualizationView.as_view(), name='api_reasoning_viz'),
    path('xai/transparency/', ModelTransparencyView.as_view(), name='api_model_transparency'),
    path('xai/explain-risk/<str:accused_id>/', ExplainableRiskView.as_view(), name='api_explain_risk'),
    path('xai/guardrails/', EthicalGuardrailsView.as_view(), name='api_ethical_guardrails'),

    # Authentication Endpoints
    path('auth/login/', LoginView.as_view(), name='auth_login'),
    path('auth/refresh/', RefreshView.as_view(), name='auth_token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),

    # Case Report Export (PDF Generation)
    path('cases/<int:pk>/report/', CaseReportView.as_view(), name='case_pdf_report'),
]
