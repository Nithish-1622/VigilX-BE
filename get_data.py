import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(os.path.join('e:\\VigilX-BE', '.env'))
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute("SELECT crimeno, casemasterid FROM casemaster LIMIT 1")
row = cur.fetchone()
print(f'FIR: {row[0]}, ID: {row[1]}')
cur.execute(f"SELECT accusedname FROM accused WHERE casemasterid={row[1]} LIMIT 1")
print(f'Accused: {cur.fetchone()[0]}')
cur.execute(f"SELECT victimname FROM victim WHERE casemasterid={row[1]} LIMIT 1")
print(f'Victim: {cur.fetchone()[0]}')
