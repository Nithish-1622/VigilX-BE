import os
import django

# Set up Django environment manually
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cases.models import FIR, Accused, BankAccount, Transaction
from django.utils import timezone
from datetime import timedelta
import uuid

def run():
    print("Seeding mock data for testing...")
    
    # 1. Create FIRs
    fir1, _ = FIR.objects.get_or_create(
        fir_number="FIR-2026-001",
        defaults={
            "reported_date_time": timezone.now(),
            "crime_type": "Theft",
            "location": "North District, Sector 4",
            "status": "Pending",
            "description": "Break-in at a commercial warehouse."
        }
    )
    
    fir2, _ = FIR.objects.get_or_create(
        fir_number="FIR-2026-002",
        defaults={
            "reported_date_time": timezone.now() - timedelta(days=15),
            "crime_type": "Fraud",
            "location": "Central District, Financial Sector",
            "status": "Pending",
            "description": "Wire transfer fraud involving offshore accounts."
        }
    )

    # 2. Create Accused
    accused1, _ = Accused.objects.get_or_create(
        name="John Doe",
        defaults={
            "age": 34,
            "gender": "M",
            "address": "123 North St",
            "status": "Arrested",
            "fir": fir1
        }
    )

    # 3. Create Bank Accounts
    account1, _ = BankAccount.objects.get_or_create(
        account_number="AC-778-999-1",
        defaults={
            "bank_name": "Global Secure Bank",
            "accused": accused1
        }
    )
    account2, _ = BankAccount.objects.get_or_create(
        account_number="EXT-9001",
        defaults={
            "bank_name": "Offshore Holdings Inc"
        }
    )

    # 4. Create Transactions
    Transaction.objects.get_or_create(
        source_account=account1,
        target_account=account2,
        amount=15000.00,
        timestamp=timezone.now(),
        is_suspicious=True
    )

    print("✅ Seeded FIRs, Accused, BankAccounts, and Transactions!")
    print("✅ All analytical and profiling endpoints will now return populated JSON data.")

if __name__ == '__main__':
    run()
