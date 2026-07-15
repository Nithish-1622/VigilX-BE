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

urlpatterns = [
    # Include default router URLs
    path('', include(router.urls)),

    # Authentication Endpoints
    path('auth/login/', LoginView.as_view(), name='auth_login'),
    path('auth/refresh/', RefreshView.as_view(), name='auth_token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),

    # Case Report Export (PDF Generation)
    path('cases/<uuid:pk>/report/', CaseReportView.as_view(), name='case_pdf_report'),
]
