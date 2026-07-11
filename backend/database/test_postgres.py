import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load the .env file from the same directory
load_dotenv()

def test_pg_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in .env file.")
        sys.exit(1)
        
    print(f"Attempting to connect to: {db_url.split('@')[1]}...")
    
    try:
        conn = psycopg2.connect(db_url)
        print("✅ SUCCESS! Connected to Neon PostgreSQL Database!")
        
        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print(f"📊 Database Version: {db_version[0]}")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_pg_connection()
