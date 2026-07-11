from django.db import models
from apps.common.models import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()

class CrimeType(models.TextChoices):
    THEFT = 'THEFT', 'Theft'
    BURGLARY = 'BURGLARY', 'Burglary'
    ROBBERY = 'ROBBERY', 'Robbery'
    ASSAULT = 'ASSAULT', 'Assault'
    HOMICIDE = 'HOMICIDE', 'Homicide'
    CYBERCRIME = 'CYBERCRIME', 'Cybercrime'
    FRAUD = 'FRAUD', 'Fraud'
    DRUGS = 'DRUGS', 'Drugs'

class CaseStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    UNDER_INVESTIGATION = 'UNDER_INVESTIGATION', 'Under Investigation'
    SOLVED = 'SOLVED', 'Solved'
    CLOSED = 'CLOSED', 'Closed'

class GenderChoices(models.TextChoices):
    MALE = 'MALE', 'Male'
    FEMALE = 'FEMALE', 'Female'
    OTHER = 'OTHER', 'Other'
    UNKNOWN = 'UNKNOWN', 'Unknown'

class AccusedStatus(models.TextChoices):
    SUSPECT = 'SUSPECT', 'Suspect'
    ACCUSED = 'ACCUSED', 'Accused'
    ARRESTED = 'ARRESTED', 'Arrested'
    CONVICTED = 'CONVICTED', 'Convicted'

class ClueEntityType(models.TextChoices):
    PHONE_NUMBER = 'PHONE_NUMBER', 'Phone Number'
    VEHICLE_PLATE = 'VEHICLE_PLATE', 'Vehicle Plate'
    EMAIL = 'EMAIL', 'Email'
    IP_ADDRESS = 'IP_ADDRESS', 'IP Address'
    BANK_ACCOUNT = 'BANK_ACCOUNT', 'Bank Account'
    SUSPECT_NICKNAME = 'SUSPECT_NICKNAME', 'Suspect Nickname'

class FIR(BaseModel):
    fir_number = models.CharField(max_length=100, unique=True)
    crime_type = models.CharField(max_length=30, choices=CrimeType.choices, default=CrimeType.THEFT)
    incident_date_time = models.DateTimeField()
    reported_date_time = models.DateTimeField()
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=30, choices=CaseStatus.choices, default=CaseStatus.PENDING)
    description = models.TextField()
    officer_in_charge = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_cases'
    )

    def __str__(self):
        return f"{self.fir_number} ({self.crime_type})"

class Victim(BaseModel):
    fir = models.ForeignKey(FIR, on_delete=models.CASCADE, related_name='victims')
    name = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GenderChoices.choices, default=GenderChoices.UNKNOWN)
    contact_number = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    statement = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - Victim of {self.fir.fir_number}"

class Accused(BaseModel):
    fir = models.ForeignKey(FIR, on_delete=models.CASCADE, related_name='accused')
    name = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=GenderChoices.choices, default=GenderChoices.UNKNOWN)
    contact_number = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    criminal_history = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=AccusedStatus.choices, default=AccusedStatus.SUSPECT)

    def __str__(self):
        return f"{self.name} - {self.status} in {self.fir.fir_number}"

class ClueEntity(BaseModel):
    fir = models.ForeignKey(FIR, on_delete=models.CASCADE, related_name='entities')
    entity_type = models.CharField(max_length=30, choices=ClueEntityType.choices)
    value = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.entity_type}: {self.value} ({self.fir.fir_number})"
