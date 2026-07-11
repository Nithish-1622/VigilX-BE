from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.investigation.models import InvestigationLog
from api.serializers.investigation import InvestigationLogSerializer
from api.permissions.rbac import IsCaseWriteAuthorized

class InvestigationLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage investigation case diaries (logs).
    Read access is allowed for all authenticated roles.
    Write access is restricted to Investigators and Supervisors.
    Supports filtering logs by a specific case using '?fir=<case_id>'.
    """
    serializer_class = InvestigationLogSerializer
    permission_classes = [IsAuthenticated, IsCaseWriteAuthorized]

    def get_queryset(self):
        queryset = InvestigationLog.objects.all().order_by('-entry_date_time')
        fir_id = self.request.query_params.get('fir')
        if fir_id:
            queryset = queryset.filter(fir_id=fir_id)
        return queryset

    def perform_create(self, serializer):
        # Automatically assign the active logged-in user as the author of the diary entry
        serializer.save(recorded_by=self.request.user)
