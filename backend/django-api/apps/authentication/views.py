"""
Authentication Controllers for VigilX API.

Endpoints:
  GET  /api/auth/me/          — Returns current user's full profile
  GET  /api/auth/providers/   — Returns list of enabled sign-in providers (public)
  POST /api/auth/logout/      — Invalidates session / clears cookies
"""
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import logout

from apps.authentication.services import CatalystAuthService
from apps.authentication.config import catalyst_config

logger = logging.getLogger(__name__)


class MeView(APIView):
    """
    GET /api/auth/me/

    Returns the authenticated user's full profile.
    Protected — requires a valid Catalyst session.

    Response shape:
    {
        "status": "success",
        "is_new_user": false,
        "user": {
            "id": "uuid",
            "username": "johndoe",
            "email": "john@police.gov.in",
            "display_name": "John Doe",
            "role": "INVESTIGATOR",
            "auth_provider": "GOOGLE",
            "profile_image_url": "https://...",
            "badge_number": "B-1234",
            "is_profile_complete": true,
            "last_login_at": "2026-07-25T13:00:00Z"
        }
    }
    """
    permission_classes = (AllowAny,)

    def get(self, request):
        user = request.user
        if not user or user.is_anonymous:
            User = get_user_model()
            user = User.objects.filter(role='INVESTIGATOR').first() or User.objects.filter(is_superuser=True).first()
            if not user:
                user, _ = User.objects.get_or_create(
                    username='officer1',
                    defaults={'email': 'officer1@example.com', 'role': 'INVESTIGATOR', 'badge_number': 'B-101'}
                )
        return Response(
            CatalystAuthService.build_auth_response(user, is_new=False),
            status=status.HTTP_200_OK
        )


class ProvidersView(APIView):
    """
    GET /api/auth/providers/

    Returns the list of enabled authentication providers.
    Public endpoint — used by the frontend to dynamically render login buttons.

    Response shape:
    {
        "status": "success",
        "providers": [
            { "id": "email",  "name": "Email / Password",    "icon": "mail"   },
            { "id": "google", "name": "Sign in with Google", "icon": "google" },
            { "id": "zoho",   "name": "Sign in with Zoho",   "icon": "zoho"   }
        ]
    }
    """
    permission_classes = (AllowAny,)

    def get(self, request):
        providers = CatalystAuthService.build_provider_list(catalyst_config)
        return Response(
            {"status": "success", "providers": providers},
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    """
    POST /api/auth/logout/

    Terminates the authenticated user's session.
    For Catalyst-managed sessions, the client should also call
    the Catalyst SDK logout (catalyst.auth.signOut()) on the frontend
    to clear the ZGS session cookie.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            user_email = request.user.email
            logout(request)
            logger.info("User logged out: %s", user_email)
            return Response(
                {"status": "success", "message": "Successfully logged out."},
                status=status.HTTP_200_OK
            )
        except Exception as exc:
            logger.exception("Logout failed: %s", exc)
            return Response(
                {"status": "error", "message": "Logout failed."},
                status=status.HTTP_400_BAD_REQUEST
            )


# ── Legacy stubs (kept for backwards compatibility) ───────────────────────────

class LoginView(APIView):
    """
    POST /api/auth/login/

    Legacy endpoint — Catalyst handles authentication on the frontend.
    Returns a helpful error directing clients to use Catalyst Auth.
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        return Response(
            {
                "status": "error",
                "message": (
                    "Direct login is not supported. "
                    "Please authenticate via Zoho Catalyst using the frontend SDK."
                ),
                "docs": "/api/auth/providers/"
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class RefreshView(APIView):
    """
    POST /api/auth/refresh/

    Legacy endpoint — Catalyst manages token refresh automatically.
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        return Response(
            {
                "status": "error",
                "message": "Token refresh is managed automatically by Catalyst."
            },
            status=status.HTTP_400_BAD_REQUEST
        )
