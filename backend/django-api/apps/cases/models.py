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
    id = models.AutoField(primary_key=True, db_column='casemasterid')
    fir_number = models.CharField(max_length=100, db_column='crimeno', null=True, blank=True)
    description = models.TextField(db_column='brieffacts', null=True, blank=True)
    incident_date_time = models.DateTimeField(db_column='incidentfromdate', null=True, blank=True)
    reported_date_time = models.DateField(db_column='crimeregistereddate', null=True, blank=True)

    crime_type = models.CharField(max_length=50, db_column='crime_type', choices=CrimeType.choices, default=CrimeType.THEFT)
    status = models.CharField(max_length=50, db_column='status', choices=CaseStatus.choices, default=CaseStatus.PENDING)
    location = models.CharField(max_length=255, db_column='location', null=True, blank=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=6, db_column='latitude', null=True, blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=6, db_column='longitude', null=True, blank=True)
    officer_in_charge = models.ForeignKey(User, on_delete=models.SET_NULL, db_column='officer_in_charge_id', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at', null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'casemaster'

    def __str__(self):
        return f"{self.fir_number or 'Draft'} - {self.crime_type}"

class Victim(models.Model):
    id = models.AutoField(primary_key=True, db_column='victimmasterid')
    fir = models.ForeignKey(FIR, on_delete=models.CASCADE, db_column='casemasterid', related_name='victims', null=True, blank=True)
    name = models.CharField(max_length=255, db_column='victimname', null=True, blank=True)
    age = models.IntegerField(db_column='ageyear', null=True, blank=True)

    gender = models.CharField(max_length=20, db_column='gender', choices=GenderChoices.choices, default=GenderChoices.UNKNOWN)
    contact_number = models.CharField(max_length=50, db_column='contact_number', null=True, blank=True)
    address = models.TextField(db_column='address', null=True, blank=True)
    statement = models.TextField(db_column='statement', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at', null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'victim'

    def __str__(self):
        return f"Victim: {self.name} (FIR: {self.fir.fir_number if self.fir else 'None'})"

class BankAccount(models.Model):
    """
    8.1 Financial Entity Model
    Tracks bank accounts linked to suspects or victims for financial profiling.
    """
    account_number = models.CharField(max_length=50, unique=True)
    bank_name = models.CharField(max_length=100)
    accused = models.ForeignKey('Accused', on_delete=models.SET_NULL, null=True, blank=True, related_name='bank_accounts')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"

class Transaction(models.Model):
    """
    8.1 Transaction Flow Model
    Tracks money flow between BankAccounts.
    """
    source_account = models.ForeignKey(BankAccount, related_name='outgoing_transactions', on_delete=models.CASCADE)
    target_account = models.ForeignKey(BankAccount, related_name='incoming_transactions', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    timestamp = models.DateTimeField()
    is_suspicious = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.source_account} -> {self.target_account}: {self.amount}"

class Complainant(models.Model):
    id = models.AutoField(primary_key=True, db_column='complainantid')
    fir = models.ForeignKey(FIR, on_delete=models.CASCADE, db_column='casemasterid', related_name='complainants', null=True, blank=True)
    name = models.CharField(max_length=255, db_column='complainantname', null=True, blank=True)
    age = models.IntegerField(db_column='ageyear', null=True, blank=True)

    gender = models.CharField(max_length=20, db_column='gender', choices=GenderChoices.choices, default=GenderChoices.UNKNOWN)
    contact_number = models.CharField(max_length=50, db_column='contact_number', null=True, blank=True)
    address = models.TextField(db_column='address', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at', null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'complainantdetails'

    def __str__(self):
        return f"Complainant: {self.name} (FIR: {self.fir.fir_number if self.fir else 'None'})"

class Accused(models.Model):
    id = models.AutoField(primary_key=True, db_column='accusedmasterid')
    fir = models.ForeignKey(FIR, on_delete=models.CASCADE, db_column='casemasterid', related_name='accused', null=True, blank=True)
    name = models.CharField(max_length=255, db_column='accusedname', null=True, blank=True)
    age = models.IntegerField(db_column='ageyear', null=True, blank=True)

    gender = models.CharField(max_length=20, db_column='gender', choices=GenderChoices.choices, default=GenderChoices.UNKNOWN)
    contact_number = models.CharField(max_length=50, db_column='contact_number', null=True, blank=True)
    address = models.TextField(db_column='address', null=True, blank=True)
    criminal_history = models.TextField(db_column='criminal_history', null=True, blank=True)
    status = models.CharField(max_length=50, db_column='status', choices=AccusedStatus.choices, default=AccusedStatus.SUSPECT)

    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at', null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'accused'

    def __str__(self):
        return f"Accused: {self.name} (FIR: {self.fir.fir_number if self.fir else 'None'})"

class ClueEntity(BaseModel):
    fir = models.ForeignKey(FIR, on_delete=models.CASCADE, related_name='entities', null=True, blank=True)
    entity_type = models.CharField(max_length=30, choices=ClueEntityType.choices)
    value = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'cases_clueentity'

    def __str__(self):
        return f"{self.entity_type}: {self.value}"

