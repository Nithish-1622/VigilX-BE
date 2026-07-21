import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

def fix():
    with connection.cursor() as cursor:
        try:
            print("Dropping integer column...")
            cursor.execute("ALTER TABLE casemaster DROP COLUMN IF EXISTS officer_in_charge_id;")
            print("Recreating as UUID...")
            cursor.execute("ALTER TABLE casemaster ADD COLUMN officer_in_charge_id UUID;")
            print("Fixed perfectly!")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    fix()
