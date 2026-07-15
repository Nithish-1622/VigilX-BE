import os
import django
import django.utils.timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User, UserRole
from apps.cases.models import FIR, Victim, Accused, ClueEntity, CrimeType, CaseStatus, AccusedStatus, ClueEntityType

def seed():
    print("Starting Django ORM Seed...")
    
    # 1. Create or get Investigator User
    officer, created = User.objects.get_or_create(
        username='officer1',
        defaults={
            'email': 'officer1@example.com',
            'role': UserRole.INVESTIGATOR,
            'badge_number': 'B-101'
        }
    )
    if created:
        officer.set_password('Officer123!')
        officer.save()
        print("Created investigator: officer1")
    else:
        print("Investigator already exists: officer1")

    # 2. Create FIR Case
    now = django.utils.timezone.now()
    fir, created = FIR.objects.get_or_create(
        fir_number='FIR-123',
        defaults={
            'crime_type': CrimeType.THEFT,
            'incident_date_time': now,
            'reported_date_time': now,
            'location': 'Koramangala, Bengaluru',
            'latitude': 12.9348,
            'longitude': 77.6189,
            'status': CaseStatus.UNDER_INVESTIGATION,
            'description': 'The suspect John Doe stole a black leather backpack containing diamonds and a laptop near Koramangala Block 4.',
            'officer_in_charge': officer
        }
    )
    if created:
        print("Created FIR Case: FIR-123")
    else:
        print("FIR Case already exists: FIR-123")

    # 3. Create Accused
    accused, created = Accused.objects.get_or_create(
        fir=fir,
        name='John Doe',
        defaults={
            'age': 32,
            'gender': 'MALE',
            'contact_number': '9876543210',
            'address': 'No. 5, 2nd Cross, Koramangala',
            'criminal_history': 'Prior arrest for robbery in 2024.',
            'status': AccusedStatus.SUSPECT
        }
    )
    if created:
        print("Created Accused: John Doe")
    else:
        print("Accused already exists: John Doe")

    # 4. Create Victim
    victim, created = Victim.objects.get_or_create(
        fir=fir,
        name='Jane Smith',
        defaults={
            'age': 28,
            'gender': 'FEMALE',
            'contact_number': '8765432109',
            'address': 'Flat 202, Sunshine Apartments, Bengaluru',
            'statement': 'I was walking near the park when a man in a black jacket grabbed my backpack and ran away.'
        }
    )
    if created:
        print("Created Victim: Jane Smith")
    else:
        print("Victim already exists: Jane Smith")

    # 5. Create Clue Entity
    entity, created = ClueEntity.objects.get_or_create(
        fir=fir,
        entity_type=ClueEntityType.PHONE_NUMBER,
        value='9876543210',
        defaults={
            'description': 'Phone number associated with suspect John Doe.'
        }
    )
    if created:
        print("Created ClueEntity: PHONE_NUMBER 9876543210")
    else:
        print("ClueEntity already exists: 9876543210")

    print("[SUCCESS] Seed complete!")

if __name__ == '__main__':
    seed()
