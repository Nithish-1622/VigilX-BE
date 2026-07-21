import os
from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth.models import User

class ServiceTokenAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication class that allows the internal FastAPI AI Engine
    to securely communicate with the Django REST Framework endpoints using
    a static, highly-secure Internal Service Token.
    """
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None

        token = parts[1]
        
        # Check against the secure internal token defined in .env
        expected_token = os.getenv("AI_ENGINE_DOWNSTREAM_SERVICE_TOKEN")
        
        if expected_token and token == expected_token:
            # Get or create a proxy "AI Engine User"
            user, _ = User.objects.get_or_create(username='ai_engine_service', defaults={'is_staff': True})
            return (user, None)

        return None
