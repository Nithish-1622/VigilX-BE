from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid


class UserRole(models.TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    INVESTIGATOR = 'INVESTIGATOR', 'Investigator'
    ANALYST = 'ANALYST', 'Crime Analyst'
    SUPERVISOR = 'SUPERVISOR', 'Supervisor'
    POLICYMAKER = 'POLICYMAKER', 'Policymaker'
    USER = 'USER', 'User'


class AuthProvider(models.TextChoices):
    EMAIL = 'EMAIL', 'Email / Password'
    GOOGLE = 'GOOGLE', 'Google'
    ZOHO = 'ZOHO', 'Zoho'
    INTERNAL = 'INTERNAL', 'Internal Service'


class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Core role
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.INVESTIGATOR
    )
    badge_number = models.CharField(max_length=50, unique=True, null=True, blank=True)

    # ── Catalyst Identity Fields ─────────────────────────────────────────────
    catalyst_user_id = models.CharField(
        max_length=100, unique=True, null=True, blank=True,
        help_text="Zoho Catalyst User ID (from Catalyst Auth)"
    )
    auth_provider = models.CharField(
        max_length=20,
        choices=AuthProvider.choices,
        default=AuthProvider.EMAIL,
        help_text="Authentication provider used on first login"
    )
    display_name = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Full display name from Catalyst / OAuth provider"
    )
    profile_image_url = models.URLField(
        max_length=1024, null=True, blank=True,
        help_text="Avatar URL from Google/Zoho profile"
    )

    # ── Audit / Session Fields ───────────────────────────────────────────────
    last_login_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Most recent successful authentication timestamp"
    )
    is_profile_complete = models.BooleanField(
        default=False,
        help_text="True after user completes onboarding (e.g. sets badge number)"
    )
    created_via_catalyst = models.BooleanField(
        default=False,
        help_text="True if this account was auto-created on first Catalyst login"
    )

    objects = UserManager()

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.username} ({self.role})"

    def get_profile_dict(self):
        """Returns a standardized profile dict for API responses."""
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "display_name": self.display_name or self.get_full_name() or self.username,
            "role": self.role,
            "auth_provider": self.auth_provider,
            "profile_image_url": self.profile_image_url,
            "badge_number": self.badge_number,
            "is_profile_complete": self.is_profile_complete,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }
