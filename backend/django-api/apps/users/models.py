from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import uuid

class UserRole(models.TextChoices):
    INVESTIGATOR = 'INVESTIGATOR', 'Investigator'
    ANALYST = 'ANALYST', 'Crime Analyst'
    SUPERVISOR = 'SUPERVISOR', 'Supervisor'
    POLICYMAKER = 'POLICYMAKER', 'Policymaker'

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
        extra_fields.setdefault('role', UserRole.SUPERVISOR)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.INVESTIGATOR
    )
    badge_number = models.CharField(max_length=50, unique=True, null=True, blank=True)

    objects = UserManager()

    def __str__(self):
        return f"{self.username} ({self.role})"
