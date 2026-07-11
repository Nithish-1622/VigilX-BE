from rest_framework import serializers
from apps.investigation.models import InvestigationLog
from api.serializers.auth import UserSerializer

class InvestigationLogSerializer(serializers.ModelSerializer):
    recorded_by_details = UserSerializer(source='recorded_by', read_only=True)

    class Meta:
        model = InvestigationLog
        fields = ('id', 'fir', 'entry_date_time', 'notes', 'recorded_by', 'recorded_by_details', 'created_at', 'updated_at')
        read_only_fields = ('id', 'entry_date_time', 'created_at', 'updated_at', 'recorded_by_details')
