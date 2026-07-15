from rest_framework import serializers
from apps.audit.models import AuditLog
from api.serializers.auth import UserSerializer

class AuditLogSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = AuditLog
        fields = ('id', 'user', 'user_details', 'action', 'timestamp', 'ip_address', 'details')
        read_only_fields = ('id', 'timestamp', 'user_details')
