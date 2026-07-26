"""
RBAC Permission Classes for VigilX Django REST API.

Role hierarchy (highest → lowest):
  ADMIN > SUPERVISOR > INVESTIGATOR = ANALYST > POLICYMAKER > USER

All classes inherit from BasePermission and follow DRF conventions.
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.users.models import UserRole


# ── Role hierarchy (used by HasMinimumRole) ───────────────────────────────────

ROLE_HIERARCHY = {
    UserRole.ADMIN: 6,
    UserRole.SUPERVISOR: 5,
    UserRole.INVESTIGATOR: 4,
    UserRole.ANALYST: 4,
    UserRole.POLICYMAKER: 2,
    UserRole.USER: 1,
}


def _has_role(request, *roles) -> bool:
    """Helper: returns True if the authenticated user has one of the given roles."""
    return (
        bool(request.user)
        and request.user.is_authenticated
        and request.user.role in roles
    )


# ── Concrete Role Permissions ─────────────────────────────────────────────────

class IsAdmin(BasePermission):
    """Allows access only to Admins (full system access)."""
    message = "Admin privileges required."

    def has_permission(self, request, view):
        return _has_role(request, UserRole.ADMIN)


class IsSupervisor(BasePermission):
    """Allows access only to Supervisors (and Admins via hierarchy)."""
    message = "Supervisor privileges required."

    def has_permission(self, request, view):
        return _has_role(request, UserRole.SUPERVISOR, UserRole.ADMIN)


class IsInvestigator(BasePermission):
    """Allows access only to Investigators."""
    message = "Investigator role required."

    def has_permission(self, request, view):
        return _has_role(request, UserRole.INVESTIGATOR, UserRole.SUPERVISOR, UserRole.ADMIN)


class IsAnalyst(BasePermission):
    """Allows access only to Crime Analysts."""
    message = "Crime Analyst role required."

    def has_permission(self, request, view):
        return _has_role(request, UserRole.ANALYST, UserRole.SUPERVISOR, UserRole.ADMIN)


class IsPolicymaker(BasePermission):
    """Allows access only to Policymakers (read-only by convention)."""
    message = "Policymaker role required."

    def has_permission(self, request, view):
        return _has_role(request, UserRole.POLICYMAKER, UserRole.SUPERVISOR, UserRole.ADMIN)


# ── Composite / Context-aware Permissions ─────────────────────────────────────

class HasMinimumRole(BasePermission):
    """
    Generic role-hierarchy checker.

    Usage:
        permission_classes = [HasMinimumRole]
        # In the view's get_permissions():
        return [HasMinimumRole.requiring(UserRole.ANALYST)]

    Or instantiate directly as a closure:
        permission_classes = [HasMinimumRole.requiring(UserRole.SUPERVISOR)]
    """
    _minimum_level: int = 0
    message = "Insufficient role privileges."

    @classmethod
    def requiring(cls, min_role: str):
        """
        Factory: returns a permission class that requires at least `min_role`.
        Example: HasMinimumRole.requiring(UserRole.ANALYST)
        """
        min_level = ROLE_HIERARCHY.get(min_role, 0)

        class _RoleCheck(cls):
            _minimum_level = min_level
            message = f"Role of {min_role} or higher is required."

        return _RoleCheck

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        user_level = ROLE_HIERARCHY.get(request.user.role, 0)
        return user_level >= self._minimum_level


class IsCaseWriteAuthorized(BasePermission):
    """
    Allows write operations (POST, PUT, PATCH, DELETE) only for
    Investigators, Supervisors, and Admins.
    All authenticated roles can read (GET, HEAD, OPTIONS).
    """
    message = "Write access requires Investigator, Supervisor, or Admin role."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        # All authenticated users can read
        if request.method in SAFE_METHODS:
            return True

        # Write access requires elevated roles
        return request.user.role in [
            UserRole.ADMIN,
            UserRole.SUPERVISOR,
            UserRole.INVESTIGATOR,
        ]


class DenyPolicymakerPII(BasePermission):
    """
    Blocks Policymakers from accessing victim/accused PII endpoints.
    Policymakers work only with aggregate/anonymised data.
    """
    message = "Policymakers are not permitted to access personal identity information."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        return request.user.role != UserRole.POLICYMAKER
