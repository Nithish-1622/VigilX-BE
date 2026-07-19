from rest_framework import serializers
from apps.cases.models import FIR, Victim, Accused, ClueEntity, Complainant
from api.serializers.auth import UserSerializer
from apps.users.models import UserRole

class ClueEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClueEntity
        fields = ('id', 'fir', 'entity_type', 'value', 'description', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class VictimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Victim
        fields = ('id', 'fir', 'name', 'age', 'gender', 'contact_number', 'address', 'statement', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        # Redact PII fields if the user has the POLICYMAKER role
        if request and request.user and getattr(request.user, 'role', None) == UserRole.POLICYMAKER:
            ret['contact_number'] = '[REDACTED]'
            ret['address'] = '[REDACTED]'
            ret['statement'] = '[REDACTED]'
        return ret

class ComplainantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complainant
        fields = ('id', 'fir', 'name', 'age', 'gender', 'contact_number', 'address', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user and getattr(request.user, 'role', None) == UserRole.POLICYMAKER:
            ret['contact_number'] = '[REDACTED]'
            ret['address'] = '[REDACTED]'
        return ret

class AccusedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accused
        fields = ('id', 'fir', 'name', 'age', 'gender', 'contact_number', 'address', 'criminal_history', 'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        # Redact PII fields if the user has the POLICYMAKER role
        if request and request.user and getattr(request.user, 'role', None) == UserRole.POLICYMAKER:
            ret['contact_number'] = '[REDACTED]'
            ret['address'] = '[REDACTED]'
            ret['criminal_history'] = '[REDACTED]'
        return ret

class FIRSerializer(serializers.ModelSerializer):
    officer_in_charge_details = UserSerializer(source='officer_in_charge', read_only=True)

    class Meta:
        model = FIR
        fields = (
            'id', 'fir_number', 'crime_type', 'incident_date_time', 'reported_date_time',
            'location', 'latitude', 'longitude', 'status', 'description', 'officer_in_charge',
            'officer_in_charge_details', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'officer_in_charge_details')

class FIRDetailSerializer(serializers.ModelSerializer):
    officer_in_charge_details = UserSerializer(source='officer_in_charge', read_only=True)
    victims = VictimSerializer(many=True, read_only=True)
    accused = AccusedSerializer(many=True, read_only=True)
    complainants = ComplainantSerializer(many=True, read_only=True)

    class Meta:
        model = FIR
        fields = (
            'id', 'fir_number', 'crime_type', 'incident_date_time', 'reported_date_time',
            'location', 'latitude', 'longitude', 'status', 'description', 'officer_in_charge',
            'officer_in_charge_details', 'victims', 'accused', 'complainants', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'officer_in_charge_details', 'victims', 'accused', 'complainants')
