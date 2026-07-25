"""
CatalystAuthService — Core authentication service layer.

Responsible for:
  - Verifying incoming requests against Zoho Catalyst (via zcatalyst-sdk)
  - Extracting and normalising user identity from Catalyst user objects
  - Building standardised auth responses
  - Handling session/token invalidation
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CatalystAuthService:
    """
    Service layer that wraps the zcatalyst-sdk authentication component.

    Usage:
        user_data = CatalystAuthService.verify_request(django_request)
        if user_data:
            # authenticated — proceed
    """

    @staticmethod
    def verify_request(request) -> Optional[dict]:
        """
        Validate the incoming request against Zoho Catalyst.

        Catalyst automatically injects session identity via cookies or
        the Authorization header when the request passes through the ZGS gateway.

        Returns the Catalyst user dict on success, or None if not authenticated.
        Expected keys in the returned dict:
            - user_id         : Catalyst's internal user ID
            - email_id        : Verified email address
            - first_name      : First name
            - last_name       : Last name
            - platform        : 'email' | 'google' | 'zoho'
            - role_details    : { role_id, role_name }
            - time_zone       : User's timezone string
        """
        try:
            import zcatalyst_sdk  # type: ignore

            # The SDK requires the raw WSGI request object
            # DRF wraps it, so we need to unwrap it
            raw_request = getattr(request, "_request", request)
            app = zcatalyst_sdk.initialize(req=raw_request)
            auth_service = app.authentication()
            user_data = auth_service.get_current_user()

            if not user_data:
                return None

            # Normalise the response — Catalyst may return nested or flat dicts
            if isinstance(user_data, dict):
                return user_data

            # Some SDK versions return an object — convert to dict
            if hasattr(user_data, "__dict__"):
                return vars(user_data)

            return None

        except ImportError:
            logger.warning("zcatalyst-sdk not installed — Catalyst auth unavailable")
            return None
        except Exception as exc:
            # Any SDK exception = token invalid or missing
            logger.debug("Catalyst token validation failed: %s", exc)
            return None

    @staticmethod
    def extract_provider(catalyst_user: dict) -> str:
        """
        Extract and normalise the authentication provider name.

        Catalyst's 'platform' field values vary by SDK version.
        Normalise all variants to: 'email', 'google', or 'zoho'
        """
        platform = str(catalyst_user.get("platform") or "email").lower().strip()

        if "google" in platform:
            return "google"
        elif "zoho" in platform:
            return "zoho"
        else:
            return "email"

    @staticmethod
    def build_auth_response(user, is_new: bool = False) -> dict:
        """
        Build a standardised authentication response payload.

        This is the canonical shape returned by all auth endpoints.
        """
        return {
            "status": "success",
            "is_new_user": is_new,
            "user": user.get_profile_dict(),
        }

    @staticmethod
    def build_provider_list(config) -> list[dict]:
        """
        Build the list of enabled sign-in providers for the frontend.

        Used by GET /api/auth/providers/ so the frontend can dynamically
        render the correct login buttons without hardcoding provider names.
        """
        providers = []

        if config.is_email_enabled:
            providers.append({
                "id": "email",
                "name": "Email / Password",
                "icon": "mail",
            })
        if config.is_google_enabled:
            providers.append({
                "id": "google",
                "name": "Sign in with Google",
                "icon": "google",
            })
        if config.is_zoho_enabled:
            providers.append({
                "id": "zoho",
                "name": "Sign in with Zoho",
                "icon": "zoho",
            })

        return providers
