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
      1. Call CatalystAuthService.verify_request() to validate the Catalyst
         session cookie / Authorization header against Zoho's servers.
      2. Call UserRepository.get_or_create_from_catalyst() to mirror the
         authenticated user into the local Django DB.
      3. Update the last_login_at timestamp.
      4. Attach the local User object to request.user.

    Supports Email/Password, Google Sign-In, and Zoho Sign-In transparently —
    the provider is detected from the Catalyst user dict and stored on the user.
    """
    def authenticate(self, request):
        from apps.authentication.services import CatalystAuthService
        from apps.users.repository import UserRepository

        # Attempt Catalyst SDK validation
        catalyst_user = CatalystAuthService.verify_request(request)
        if not catalyst_user:
            return None  # Not a Catalyst-authenticated request — pass to next class

        try:
            user, is_new = UserRepository.get_or_create_from_catalyst(catalyst_user)
            UserRepository.update_last_login(user)

            if is_new:
                logger.info(
                    "First login: new user synced to local DB — %s (provider=%s)",
                    user.email,
                    user.auth_provider,
                )

            return (user, None)

        except ValueError as exc:
            logger.error("Catalyst auth DB sync failed: %s", exc)
            raise exceptions.AuthenticationFailed("Could not sync user from Catalyst.")
        except Exception as exc:
            logger.exception("Unexpected error during Catalyst authentication: %s", exc)
            raise exceptions.AuthenticationFailed("Authentication error.")

    def authenticate_header(self, request):
        """
        Returned in WWW-Authenticate header on 401 responses.
        Tells the client to use Catalyst Bearer tokens.
        """
        return 'CatalystAuth realm="VigilX API"'
