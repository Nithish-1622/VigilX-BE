from django.db import models
from apps.common.models import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()

class CrimeType(models.TextChoices):
    THEFT = 'THEFT', 'Theft'
    BURGLARY = 'BURGLARY', 'Burglary'
    ROBBERY = 'ROBBERY', 'Robbery'

class CaseStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    UNDER_INVESTIGATION = 'UNDER_INVESTIGATION', 'Under Investigation'

class GenderChoices(models.TextChoices):
    MALE = 'MALE', 'Male'
    FEMALE = 'FEMALE', 'Female'
    UNKNOWN = 'UNKNOWN', 'Unknown'

class AccusedStatus(models.TextChoices):
    SUSPECT = 'SUSPECT', 'Suspect'
    ACCUSED = 'ACCUSED', 'Accused'

class ClueEntityType(models.TextChoices):
    PHONE_NUMBER = 'PHONE_NUMBER', 'Phone Number'

class FIR(models.Model):
    id = models.IntegerField(primary_key=True, db_column='casemasterid')
    fir_number = models.CharField(max_length=100, db_column='crimeno', null=True, blank=True)
    description = models.TextField(db_column='brieffacts', null=True, blank=True)
    incident_date_time = models.DateTimeField(db_column='incidentfromdate', null=True, blank=True)
    reported_date_time = models.DateTimeField(db_column='crimeregistereddate', null=True, blank=True)

    @property
    def crime_type(self): return CrimeType.THEFT
    @property
    def status(self): return CaseStatus.PENDING
    @property
    def location(self): return None
    @property
    def latitude(self): return None
    @property
    def longitude(self): return None
    @property
    def officer_in_charge(self): return None
    @property
    def created_at(self): return self.reported_date_time
    @property
    def updated_at(self): return self.reported_date_time

    class Meta:
        managed = False
        db_table = 'casemaster'

class Victim(models.Model):
    id = models.IntegerField(primary_key=True, db_column='victimmasterid')
    fir = models.ForeignKey(FIR, on_delete=models.CASCADE, db_column='casemasterid', related_name='victims', null=True, blank=True)
    name = models.CharField(max_length=255, db_column='victimname', null=True, blank=True)
    age = models.IntegerField(db_column='ageyear', null=True, blank=True)

    @property
    def gender(self): return GenderChoices.UNKNOWN
    @property
    def contact_number(self): return None
    @property
    def address(self): return None
    @property
    def statement(self): return None
    @property
    def created_at(self): return None
    @property
    def updated_at(self): return None

    class Meta:
        managed = False
        db_table = 'victim'

class Complainant(models.Model):
    id = models.IntegerField(primary_key=True, db_column='complainantid')
    fir = models.ForeignKey(FIR, on_delete=models.CASCADE, db_column='casemasterid', related_name='complainants', null=True, blank=True)
    name = models.CharField(max_length=255, db_column='complainantname', null=True, blank=True)
    age = models.IntegerField(db_column='ageyear', null=True, blank=True)

    @property
    def gender(self): return GenderChoices.UNKNOWN
    @property
    def contact_number(self): return None
    @property
    def address(self): return None
    @property
    def created_at(self): return None
    @property
    def updated_at(self): return None

    class Meta:
        managed = False
        db_table = 'complainantdetails'

class Accused(models.Model):
    id = models.IntegerField(primary_key=True, db_column='accusedmasterid')
    fir = models.ForeignKey(FIR, on_delete=models.CASCADE, db_column='casemasterid', related_name='accused', null=True, blank=True)
    name = models.CharField(max_length=255, db_column='accusedname', null=True, blank=True)
    age = models.IntegerField(db_column='ageyear', null=True, blank=True)

    @property
    def gender(self): return GenderChoices.UNKNOWN
    @property
    def contact_number(self): return None
    @property
    def address(self): return None
    @property
    def criminal_history(self): return None
    @property
    def status(self): return AccusedStatus.SUSPECT
    @property
    def created_at(self): return None
    @property
    def updated_at(self): return None

    class Meta:
        managed = False
        db_table = 'accused'

class ClueEntity(BaseModel):
    fir = models.ForeignKey(FIR, on_delete=models.CASCADE, related_name='entities', null=True, blank=True)
    entity_type = models.CharField(max_length=30, choices=ClueEntityType.choices)
    value = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'cases_clueentity'
