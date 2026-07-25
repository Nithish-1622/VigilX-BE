import os
# pyrefly: ignore [missing-import]
from rest_framework import authentication
# pyrefly: ignore [missing-import]
from rest_framework import exceptions
# pyrefly: ignore [missing-import]
from django.contrib.auth import get_user_model

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
            User = get_user_model()
            user, _ = User.objects.get_or_create(username='ai_engine_service', defaults={'is_staff': True, 'is_superuser': True})
            return (user, None)

        return None

class DevModeBypassAuthentication(authentication.BaseAuthentication):
    """
    Bypasses authentication during testing if DEV_MODE=TRUE.
    """
    def authenticate(self, request):
        if os.getenv("DEV_MODE", "FALSE").upper() == "TRUE":
            User = get_user_model()
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                user, _ = User.objects.get_or_create(username='dev_admin', defaults={'is_staff': True, 'is_superuser': True})
            return (user, None)
        return None

class CatalystAuthentication(authentication.BaseAuthentication):
    """
    Native Zoho Catalyst Authentication. 
    Reads the incoming request, parses the Zoho Session Cookie (zcsession) or Authorization header,
    validates it using the zcatalyst-sdk, and returns the authenticated Django User.
    """
    def authenticate(self, request):
        try:
            import zcatalyst_sdk
            # zcatalyst_sdk requires the raw WSGI environ request to read headers/cookies
            app = zcatalyst_sdk.initialize(req=request._request)
            auth_service = app.authentication()
            user_details = auth_service.get_current_user()
            
            if user_details:
                # Zoho Catalyst returns email_id, role_details, etc.
                email = user_details.get('email_id')
                if not email:
                    return None
                    
                User = get_user_model()
                # Mirror the Zoho user in the local Django DB for relational foreign keys
                user, created = User.objects.get_or_create(username=email, defaults={'email': email})
                
                # Optionally sync roles
                role = user_details.get('role_details', {}).get('role_name')
                if role == 'Admin' and not user.is_superuser:
                    user.is_superuser = True
                    user.is_staff = True
                    user.save()
                    
                return (user, None)
        except Exception as e:
            # If token is missing or invalid, Catalyst SDK throws an exception
            pass
            
        return None
