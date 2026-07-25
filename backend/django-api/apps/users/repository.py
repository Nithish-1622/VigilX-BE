"""
UserRepository — Data access layer for User model operations.

All database interactions related to user lifecycle management are
centralized here to keep views and services free of raw ORM queries.
"""
import logging
from django.utils import timezone
from .models import User, UserRole, AuthProvider

logger = logging.getLogger(__name__)

# Map Catalyst role names → VigilX internal roles
CATALYST_ROLE_MAP = {
    "App Administrator": UserRole.ADMIN,
    "Admin": UserRole.ADMIN,
    "Supervisor": UserRole.SUPERVISOR,
    "Investigator": UserRole.INVESTIGATOR,
    "Crime Analyst": UserRole.ANALYST,
    "Analyst": UserRole.ANALYST,
    "Policymaker": UserRole.POLICYMAKER,
    "User": UserRole.USER,
}

# Map Catalyst provider strings → AuthProvider enum
CATALYST_PROVIDER_MAP = {
    "zoho": AuthProvider.ZOHO,
    "google": AuthProvider.GOOGLE,
    "email": AuthProvider.EMAIL,
    "EMAIL": AuthProvider.EMAIL,
}


class UserRepository:
    """
    Central repository for all User DB operations.
    Call `get_or_create_from_catalyst()` on every authenticated request
    to keep the local user mirror up to date.
    """

    @staticmethod
    def get_or_create_from_catalyst(catalyst_user: dict) -> tuple[User, bool]:
        """
        Upsert a user record from Catalyst user data.

        Returns (user, created) where `created` is True on first login.
        Handles cross-provider email linking automatically — if a user
        signs in via Google with the same email they used for Email/Password,
        the existing record is returned and the provider is updated.
        """
        email = (catalyst_user.get("email_id") or "").strip().lower()
        catalyst_uid = str(catalyst_user.get("user_id") or "").strip()
        first_name = catalyst_user.get("first_name", "")
        last_name = catalyst_user.get("last_name", "")
        display_name = f"{first_name} {last_name}".strip() or email

        # Determine provider from Catalyst response
        platform_str = str(catalyst_user.get("platform", "email")).lower()
        auth_provider = CATALYST_PROVIDER_MAP.get(platform_str, AuthProvider.EMAIL)

        # Determine role from Catalyst role_details
        role_details = catalyst_user.get("role_details") or {}
        role_name = role_details.get("role_name", "Investigator")
        role = CATALYST_ROLE_MAP.get(role_name, UserRole.INVESTIGATOR)

        if not email:
            raise ValueError("Catalyst user has no email — cannot sync to local DB")

        # ── 1. Try to find by Catalyst UID (fastest path) ────────────────────
        user = User.objects.filter(catalyst_user_id=catalyst_uid).first() if catalyst_uid else None

        # ── 2. Fall back to email lookup (cross-provider linking) ─────────────
        if user is None:
            user = User.objects.filter(email=email).first()

        if user is not None:
            # Update mutable fields that may have changed
            changed = False
            if catalyst_uid and user.catalyst_user_id != catalyst_uid:
                user.catalyst_user_id = catalyst_uid
                changed = True
            if user.display_name != display_name:
                user.display_name = display_name
                changed = True
            if user.role != role:
                user.role = role
                user.is_staff = role in [UserRole.ADMIN, UserRole.SUPERVISOR]
                user.is_superuser = role == UserRole.ADMIN
                changed = True
            if changed:
                user.save(update_fields=[
                    "catalyst_user_id", "display_name", "role",
                    "is_staff", "is_superuser"
                ])
            logger.debug("Catalyst auth: existing user found — %s", email)
            return user, False

        # ── 3. Create new user (first login) ─────────────────────────────────
        username = email.split("@")[0]
        # Ensure username uniqueness
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create(
            username=username,
            email=email,
            catalyst_user_id=catalyst_uid or None,
            auth_provider=auth_provider,
            display_name=display_name,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_staff=role in [UserRole.ADMIN, UserRole.SUPERVISOR],
            is_superuser=role == UserRole.ADMIN,
            is_active=True,
            created_via_catalyst=True,
        )
        logger.info("Catalyst auth: new user created — %s (role=%s, provider=%s)", email, role, auth_provider)
        return user, True

    @staticmethod
    def update_last_login(user: User) -> None:
        """Update the last_login_at timestamp. Called on every authenticated request."""
        User.objects.filter(pk=user.pk).update(last_login_at=timezone.now())

    @staticmethod
    def get_by_email(email: str) -> User | None:
        """Fetch a user by email address (case-insensitive)."""
        return User.objects.filter(email__iexact=email).first()

    @staticmethod
    def get_by_catalyst_uid(uid: str) -> User | None:
        """Fetch a user by their Catalyst UID."""
        return User.objects.filter(catalyst_user_id=uid).first()
