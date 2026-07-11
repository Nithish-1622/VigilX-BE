from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.users.models import UserRole

class IsSupervisor(BasePermission):
    """
    Allows access only to Supervisors.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.SUPERVISOR

class IsInvestigator(BasePermission):
    """
    Allows access only to Investigators.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.INVESTIGATOR

class IsAnalyst(BasePermission):
    """
    Allows access only to Analysts.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.ANALYST

class IsPolicymaker(BasePermission):
    """
    Allows access only to Policymakers.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == UserRole.POLICYMAKER

class IsCaseWriteAuthorized(BasePermission):
    """
    Allows write operations (POST, PUT, PATCH, DELETE) only for Investigators and Supervisors.
    Allows read-only operations (GET, HEAD, OPTIONS) for all roles including Analyst and Policymaker.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Safe methods (GET, HEAD, OPTIONS) are allowed for all authenticated roles
        if request.method in SAFE_METHODS:
            return True
            
        # Write operations are restricted to Investigator and Supervisor
        return request.user.role in [UserRole.SUPERVISOR, UserRole.INVESTIGATOR]

class DenyPolicymakerPII(BasePermission):
    """
    Blocks Policymakers from accessing victim/accused details endpoints entirely
    since they are not allowed to view raw personal identity details.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Deny all access if role is Policymaker
        if request.user.role == UserRole.POLICYMAKER:
            return False
            
        return True
