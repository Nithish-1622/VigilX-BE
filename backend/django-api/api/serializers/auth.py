from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.users.models import UserRole

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'badge_number', 'is_active', 'date_joined')
        read_only_fields = ('id', 'is_active', 'date_joined')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'role', 'badge_number')

    def validate_role(self, value):
        if value not in UserRole.values:
            raise serializers.ValidationError("Invalid role option.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password'],
            role=validated_data.get('role', UserRole.INVESTIGATOR),
            badge_number=validated_data.get('badge_number')
        )
        return user
