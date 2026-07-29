"""
Authentication backends for VigilX Django REST API.

Execution order (configured in settings.py REST_FRAMEWORK):
  1. DevModeBypassAuthentication  — short-circuits in local dev (DEV_MODE=TRUE)
  2. ServiceTokenAuthentication   — for internal FastAPI ↔ Django calls
  3. CatalystAuthentication       — validates Zoho Catalyst sessions (production)
  4. SessionAuthentication        — Django session fallback
"""
import logging
import os

from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)


# ── 1. Local Development Bypass ───────────────────────────────────────────────

class DevModeBypassAuthentication(authentication.BaseAuthentication):
    """
    Bypasses all authentication checks when DEV_MODE=TRUE.

    Only active locally — the Catalyst env variable is never set to TRUE
    in production AppSail, so this class is completely inert in production.
    """
    def authenticate(self, request):
        if os.getenv("DEV_MODE", "FALSE").upper() != "TRUE":
            return None

        User = get_user_model()
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            user, _ = User.objects.get_or_create(
                username='dev_admin',
                defaults={
                    'email': 'dev@vigilx.local',
                    'is_staff': True,
                    'is_superuser': True,
                    'role': 'ADMIN',
                }
            )
        logger.debug("DevMode: bypassing auth as %s", user.username)
        return (user, None)


# ── 2. Internal Service Token ─────────────────────────────────────────────────

class ServiceTokenAuthentication(authentication.BaseAuthentication):
    """
    Allows the internal FastAPI AI Engine to call Django REST endpoints
    using a shared static secret token (AI_ENGINE_DOWNSTREAM_SERVICE_TOKEN).

    This avoids circular dependencies between services — the AI Engine does
    not need a Catalyst session to call internal Django APIs.
    """
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None

        token = parts[1]
        expected_token = os.getenv("AI_ENGINE_DOWNSTREAM_SERVICE_TOKEN")

        if not expected_token or token != expected_token:
            return None

        # Return a dedicated service proxy user
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            username='ai_engine_service',
            defaults={
                'email': 'ai-engine@vigilx.internal',
                'is_staff': True,
                'is_superuser': True,
                'auth_provider': 'INTERNAL',
            }
        )
        logger.debug("ServiceToken: AI Engine authenticated")
        return (user, None)


# ── 3. Zoho Catalyst Authentication (Primary Production Auth) ─────────────────

class CatalystAuthentication(authentication.BaseAuthentication):
    """
    Primary authentication class for production.

    Flow:
      1. CatalystAuthService.verify_request() validates the Catalyst session/cookie.
      2. CatalystUserRepository.get_or_create_from_catalyst() reads/writes the
         user profile in Zoho Catalyst Cloud SQL (NOT Neon Postgres).
      3. A lightweight proxy Django User is used ONLY for DRF compatibility.
         All real user data lives in Catalyst Cloud SQL.
    """
    def authenticate(self, request):
        from apps.authentication.services import CatalystAuthService
        from apps.authentication.catalyst_user_repository import CatalystUserRepository

        catalyst_user = CatalystAuthService.verify_request(request)
        if not catalyst_user:
            return None

        try:
            # Save / update user profile in Catalyst Cloud SQL
            profile, is_new = CatalystUserRepository.get_or_create_from_catalyst(
                catalyst_user, request=request
            )
            CatalystUserRepository.update_last_login(
                profile.get("catalyst_uid", ""), request=request
            )

            # Build a lightweight Django proxy user for DRF (no DB write to Neon)
            User = get_user_model()
            email = profile.get("email", "")
            proxy_user, _ = User.objects.get_or_create(
                username=email or profile.get("catalyst_uid", "unknown"),
                defaults={
                    "email": email,
                    "is_active": True,
                }
            )
            # Attach Catalyst Cloud SQL profile to the request user
            proxy_user.catalyst_profile = profile
            proxy_user.role = profile.get("role", "INVESTIGATOR")

            if is_new:
                logger.info(
                    "First login: new user created in Catalyst Cloud SQL — %s (role=%s)",
                    email, profile.get("role"),
                )

            return (proxy_user, None)

        except Exception as exc:
            logger.exception("CatalystAuthentication error: %s", exc)
            raise exceptions.AuthenticationFailed("Authentication error.")

    def authenticate_header(self, request):
        return 'CatalystAuth realm="VigilX API"'
