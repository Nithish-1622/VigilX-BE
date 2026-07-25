import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
tables = [r[0] for r in cur.fetchall()]
print(f"Postgres tables: {tables}")
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'casemaster'")
cols = cur.fetchall()
print(f"casemaster columns: {cols}")
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'victim'")
cols = cur.fetchall()
print(f"victim columns: {cols}")
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'accused'")
cols = cur.fetchall()
print(f"accused columns: {cols}")
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'complainantdetails'")
cols = cur.fetchall()
print(f"complainantdetails columns: {cols}")
