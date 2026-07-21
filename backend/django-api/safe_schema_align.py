import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

def add_column_if_not_exists(table_name, column_name, column_def):
    with connection.cursor() as cursor:
        try:
            # Check if column exists
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}' AND column_name='{column_name}'")
            if not cursor.fetchone():
                print(f"Adding column {column_name} to {table_name}...")
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
            else:
                print(f"Column {column_name} already exists in {table_name}.")
        except Exception as e:
            print(f"Error on {table_name}.{column_name}: {e}")

def run():
    print("Starting non-destructive schema alignment...")
    
    # CaseMaster
    add_column_if_not_exists("casemaster", "crime_type", "VARCHAR(50)")
    add_column_if_not_exists("casemaster", "status", "VARCHAR(50)")
    add_column_if_not_exists("casemaster", "location", "VARCHAR(255)")
    add_column_if_not_exists("casemaster", "officer_in_charge_id", "INTEGER")
    add_column_if_not_exists("casemaster", "created_at", "TIMESTAMP")
    add_column_if_not_exists("casemaster", "updated_at", "TIMESTAMP")

    # Victim
    add_column_if_not_exists("victim", "contact_number", "VARCHAR(50)")
    add_column_if_not_exists("victim", "address", "TEXT")
    add_column_if_not_exists("victim", "statement", "TEXT")
    add_column_if_not_exists("victim", "created_at", "TIMESTAMP")
    add_column_if_not_exists("victim", "updated_at", "TIMESTAMP")
    # Actually the PDF says genderID is INTEGER, but models.py maps `gender` to `VARCHAR(20)`. If genderID exists, maybe we need `gender`
    add_column_if_not_exists("victim", "gender", "VARCHAR(20)")

    # Accused
    add_column_if_not_exists("accused", "contact_number", "VARCHAR(50)")
    add_column_if_not_exists("accused", "address", "TEXT")
    add_column_if_not_exists("accused", "criminal_history", "TEXT")
    add_column_if_not_exists("accused", "status", "VARCHAR(50)")
    add_column_if_not_exists("accused", "created_at", "TIMESTAMP")
    add_column_if_not_exists("accused", "updated_at", "TIMESTAMP")
    add_column_if_not_exists("accused", "gender", "VARCHAR(20)")

    # ComplainantDetails
    add_column_if_not_exists("complainantdetails", "contact_number", "VARCHAR(50)")
    add_column_if_not_exists("complainantdetails", "address", "TEXT")
    add_column_if_not_exists("complainantdetails", "created_at", "TIMESTAMP")
    add_column_if_not_exists("complainantdetails", "updated_at", "TIMESTAMP")
    add_column_if_not_exists("complainantdetails", "gender", "VARCHAR(20)")

    # The missing table ClueEntity
    with connection.cursor() as cursor:
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS cases_clueentity (id SERIAL PRIMARY KEY, entity_type VARCHAR(30), value VARCHAR(255), description TEXT, casemasterid INTEGER, created_at TIMESTAMP, updated_at TIMESTAMP)")
            print("Table cases_clueentity checked.")
        except Exception as e:
            print(f"Error creating clueentity: {e}")

    print("Schema alignment complete!")

if __name__ == "__main__":
    run()
