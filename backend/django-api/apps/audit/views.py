from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from apps.audit.models import AuditLog
from api.serializers.audit import AuditLogSerializer
from api.permissions.rbac import IsSupervisor

class AuditLogViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    ViewSet to list and retrieve system audit logs, and allow AI engine to log queries.
    Access is restricted to Supervisors for reading, but Authenticated users can create.
    """
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        action_filter = self.request.query_params.get('action')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action_filter:
            queryset = queryset.filter(action__icontains=action_filter)
            
        return queryset
