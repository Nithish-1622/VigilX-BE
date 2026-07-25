import os
import random
import time
from datetime import datetime, timedelta
from faker import Faker
import psycopg2
from psycopg2.extras import execute_values
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from fastembed import TextEmbedding
from dotenv import load_dotenv

# Load .env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

fake = Faker('en_IN')
TOTAL_RECORDS = 1000

# Constants matching models.py
CRIME_TYPES = ['THEFT', 'BURGLARY', 'ROBBERY']
CASE_STATUSES = ['PENDING', 'UNDER_INVESTIGATION']
GENDERS = ['MALE', 'FEMALE', 'UNKNOWN']
ACCUSED_STATUSES = ['SUSPECT', 'ACCUSED']

def get_officer_id(conn):
    cur = conn.cursor()
    # Try to find ai_engine_service user
    cur.execute("SELECT id FROM users_user WHERE username = 'ai_engine_service' LIMIT 1")
    row = cur.fetchone()
    if row:
        return row[0]
    
    # Create if not exists (using uuid)
    print("Creating default officer 'ai_engine_service'...")
    now = datetime.now()
    import uuid
    new_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO users_user (id, password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, created_at, updated_at, role, is_verified)
        VALUES (%s, 'pbkdf2_sha256$260000$dummy', true, 'ai_engine_service', 'AI', 'Engine', 'ai@vigilx.com', true, true, %s, %s, %s, 'OFFICER', true)
        RETURNING id
    """, (new_id, now, now, now))
    conn.commit()
    return new_id

def seed_lookup_tables(conn):
    cur = conn.cursor()
    print("Ensuring lookup tables have data...")
    cur.execute("INSERT INTO State (StateID, StateName, NationalityID, Active) VALUES (1, 'Maharashtra', 1, true) ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO District (DistrictID, DistrictName, StateID, Active) VALUES (1, 'Mumbai', 1, true) ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO Court (CourtID, CourtName, DistrictID, StateID, Active) VALUES (1, 'Mumbai High Court', 1, 1, true) ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO UnitType (UnitTypeID, UnitTypeName, CityDistState, Hierarchy, Active) VALUES (1, 'Police Station', 'Mumbai', 1, true) ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO Unit (UnitID, UnitName, TypeID, ParentUnit, NationalityID, StateID, DistrictID, Active) VALUES (1, 'Central PS', 1, 1, 1, 1, 1, true) ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO Rank (RankID, RankName, Hierarchy, Active) VALUES (1, 'Inspector', 1, true) ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO Designation (DesignationID, DesignationName, Active, SortOrder) VALUES (1, 'Inspector', true, 1) ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO Employee (EmployeeID, DistrictID, UnitID, RankID, DesignationID, KGID, FirstName, EmployeeDOB, GenderID, BloodGroupID, PhysicallyChallenged, AppointmentDate) VALUES (1, 1, 1, 1, 1, 'KG123', 'Raj', '1980-01-01', 1, 1, false, '2000-01-01') ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO CaseCategory (CaseCategoryID, LookupValue) VALUES (1, 'Theft'), (2, 'Assault'), (3, 'Fraud') ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO GravityOffence (GravityOffenceID, LookupValue) VALUES (1, 'High') ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO CrimeHead (CrimeHeadID, CrimeGroupName, Active) VALUES (1, 'Theft', true) ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO CrimeSubHead (CrimeSubHeadID, CrimeHeadID, CrimeHeadName, SeqID) VALUES (1, 1, 'Theft', 1) ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO CaseStatusMaster (CaseStatusID, CaseStatusName) VALUES (1, 'Open'), (2, 'Closed'), (3, 'Pending Trial') ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO OccupationMaster (OccupationID, OccupationName) VALUES (1, 'Business') ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO ReligionMaster (ReligionID, ReligionName) VALUES (1, 'Hindu') ON CONFLICT DO NOTHING")
    cur.execute("INSERT INTO CasteMaster (caste_master_id, caste_master_name) VALUES (1, 'General') ON CONFLICT DO NOTHING")
    conn.commit()
    cur.close()

def generate_data(officer_id):
    cases = []
    victims = []
    complainants = []
    accused_list = []
    bank_accounts = []
    transactions = []
    clue_entities = []

    print(f"Generating {TOTAL_RECORDS} cases (this may take a moment)...")

    accused_id_counter = 1
    bank_account_id_counter = 1
    
    for i in range(1, TOTAL_RECORDS + 1):
        case_id = i
        fir_number = f"FIR-IN-{2026}-{case_id:04d}"
        incident_date = fake.date_time_between(start_date="-1y", end_date="now")
        reported_date = incident_date + timedelta(hours=random.randint(1, 48))
        crime_type = random.choice(CRIME_TYPES)
        status = random.choice(CASE_STATUSES)
        location = f"{fake.street_address()}, {fake.city()}"
        lat = round(random.uniform(8.0, 37.0), 6)
        lng = round(random.uniform(68.0, 97.0), 6)
        description = f"Incident of {crime_type} reported at {location}. {fake.text(max_nb_chars=200)}"
        now = datetime.now()

        # casemaster fields: casemasterid, crimeno, caseno, crimeregistereddate, policepersonid, policestationid, casecategoryid, gravityoffenceid, crimemajorheadid, crimeminorheadid, casestatusid, courtid, incidentfromdate, incidenttodate, inforeceivedpsdate, latitude, longitude, brieffacts, crime_type, status, location, created_at, updated_at, officer_in_charge_id
        cases.append((
            case_id, fir_number, fir_number, reported_date, 1, 1, random.randint(1,3), 1, 1, 1, random.randint(1,3), 1, incident_date, reported_date, reported_date, lat, lng, description, crime_type, status, location, now, now, officer_id
        ))

        # complainantdetails fields: complainantid, casemasterid, complainantname, ageyear, occupationid, religionid, casteid, genderid, contact_number, address, created_at, updated_at, gender
        complainant_id = case_id
        complainants.append((
            complainant_id, case_id, fake.name(), random.randint(20, 70), 1, 1, 1, 1, fake.phone_number()[:50], location, now, now, random.choice(GENDERS)
        ))

        # victim fields: victimmasterid, casemasterid, victimname, ageyear, genderid, victimpolice, contact_number, address, statement, created_at, updated_at, gender
        victim_id = case_id
        statement = fake.text(max_nb_chars=150)
        victims.append((
            victim_id, case_id, fake.name(), random.randint(15, 80), 1, 'Local PS', fake.phone_number()[:50], fake.address(), statement, now, now, random.choice(GENDERS)
        ))

        # accused fields: accusedmasterid, casemasterid, accusedname, ageyear, genderid, personid, contact_number, address, criminal_history, status, created_at, updated_at, gender
        acc_id = accused_id_counter
        accused_id_counter += 1
        criminal_hist = fake.sentence(nb_words=6) if random.choice([True, False]) else "No prior history."
        accused_list.append((
            acc_id, case_id, fake.name(), random.randint(18, 60), 1, str(acc_id), fake.phone_number()[:50], fake.address(), criminal_hist, random.choice(ACCUSED_STATUSES), now, now, random.choice(GENDERS)
        ))

        # Bank Account for the accused
        acc_bank_id_1 = bank_account_id_counter
        acc_bank_id_2 = bank_account_id_counter + 1
        bank_account_id_counter += 2
        
        bank_accounts.append((acc_bank_id_1, fake.bban()[:50], fake.company()[:100] + " Bank", acc_id, now))
        bank_accounts.append((acc_bank_id_2, fake.bban()[:50], fake.company()[:100] + " Bank", acc_id, now))

        # Transaction
        amount = round(random.uniform(100.0, 50000.0), 2)
        transactions.append((acc_bank_id_1, acc_bank_id_2, amount, now, random.choice([True, False])))

        # Clue Entity
        import uuid
        clue_id = str(uuid.uuid4())
        clue_entities.append((
            clue_id, case_id, 'PHONE_NUMBER', fake.phone_number()[:255], f"Found at {location} during investigation.", now, now
        ))

    return cases, victims, complainants, accused_list, bank_accounts, transactions, clue_entities

def insert_postgres(conn, data):
    cases, victims, complainants, accused_list, bank_accounts, transactions, clue_entities = data
    cur = conn.cursor()
    
    print("Inserting into Postgres...")
    
    execute_values(cur, """
        INSERT INTO casemaster (casemasterid, crimeno, caseno, crimeregistereddate, policepersonid, policestationid, casecategoryid, gravityoffenceid, crimemajorheadid, crimeminorheadid, casestatusid, courtid, incidentfromdate, incidenttodate, inforeceivedpsdate, latitude, longitude, brieffacts, crime_type, status, location, created_at, updated_at, officer_in_charge_id) 
        VALUES %s
    """, cases)

    execute_values(cur, """
        INSERT INTO complainantdetails (complainantid, casemasterid, complainantname, ageyear, occupationid, religionid, casteid, genderid, contact_number, address, created_at, updated_at, gender) 
        VALUES %s
    """, complainants)

    execute_values(cur, """
        INSERT INTO victim (victimmasterid, casemasterid, victimname, ageyear, genderid, victimpolice, contact_number, address, statement, created_at, updated_at, gender) 
        VALUES %s
    """, victims)

    execute_values(cur, """
        INSERT INTO accused (accusedmasterid, casemasterid, accusedname, ageyear, genderid, personid, contact_number, address, criminal_history, status, created_at, updated_at, gender) 
        VALUES %s
    """, accused_list)
    
    # We provide IDs explicitly so transactions can reference them
    execute_values(cur, """
        INSERT INTO cases_bankaccount (id, account_number, bank_name, accused_id, created_at) 
        VALUES %s
    """, bank_accounts)

    execute_values(cur, """
        INSERT INTO cases_transaction (source_account_id, target_account_id, amount, timestamp, is_suspicious) 
        VALUES %s
    """, transactions)

    execute_values(cur, """
        INSERT INTO cases_clueentity (id, fir_id, entity_type, value, description, created_at, updated_at) 
        VALUES %s
    """, clue_entities)

    conn.commit()
    cur.close()
    print("Postgres insertion complete.")

def insert_neo4j(data):
    cases, victims, complainants, accused_list, _, _, _ = data
    
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    print("Inserting into Neo4j...")
    with driver.session() as session:
        # Cases
        case_data = [{"case_id": f"FIR_{c[0]}", "case_number": c[1], "status": c[6]} for c in cases]
        session.run("""
            UNWIND $cases AS c
            CREATE (case:Case {id: c.case_id, case_number: c.case_number, status: c.status})
        """, cases=case_data)

        # Complainants
        comp_data = [{"person_id": f"COMP_{c[0]}", "name": c[2], "age_group": str(c[3]), "case_id": f"FIR_{c[1]}"} for c in complainants]
        session.run("""
            UNWIND $comps AS c
            CREATE (p:Person {id: c.person_id, name: c.name, age_group: c.age_group, type: 'Complainant'})
            WITH p, c
            MATCH (case:Case {id: c.case_id})
            CREATE (p)-[:FILED_BY]->(case)
        """, comps=comp_data)

        # Victims
        vic_data = [{"person_id": f"VIC_{v[0]}", "name": v[2], "age_group": str(v[3]), "case_id": f"FIR_{v[1]}"} for v in victims]
        session.run("""
            UNWIND $vics AS v
            CREATE (p:Person {id: v.person_id, name: v.name, age_group: v.age_group, type: 'Victim'})
            WITH p, v
            MATCH (case:Case {id: v.case_id})
            CREATE (p)-[:VICTIM_OF]->(case)
        """, vics=vic_data)

        # Accused
        acc_data = [{"person_id": f"ACC_{a[0]}", "name": a[2], "age_group": str(a[3]), "case_id": f"FIR_{a[1]}"} for a in accused_list]
        session.run("""
            UNWIND $accs AS a
            CREATE (p:Person {id: a.person_id, name: a.name, age_group: a.age_group, type: 'Accused'})
            WITH p, a
            MATCH (case:Case {id: a.case_id})
            CREATE (p)-[:ACCUSED_IN]->(case)
        """, accs=acc_data)
        
    driver.close()
    print("Neo4j insertion complete.")

def insert_qdrant(data):
    cases = data[0]
    print("Generating Qdrant embeddings (this will take a minute or two for 1000 records)...")
    
    host = os.getenv("QDRANT_HOST")
    api_key = os.getenv("QDRANT_API_KEY")
    client = QdrantClient(url=host, api_key=api_key)
    
    # Create collections if they don't exist
    for col in ["vigilx_cases", "crime_cases"]:
        try:
            client.create_collection(collection_name=col, vectors_config=VectorParams(size=384, distance=Distance.COSINE))
        except:
            pass # Already exists
            
    embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    # Batch embeddings to avoid memory spikes
    batch_size = 100
    for i in range(0, len(cases), batch_size):
        batch = cases[i:i+batch_size]
        docs = [c[2] for c in batch] # c[2] is brieffacts
        embeddings = list(embedding_model.embed(docs))
        
        points = []
        for idx, case in enumerate(batch):
            points.append(PointStruct(
                id=case[0],
                vector=embeddings[idx].tolist(),
                payload={
                    "case_id": f"FIR_{case[0]}",
                    "case_no": case[1],
                    "brief_facts": case[2]
                }
            ))
            
        client.upsert(collection_name="vigilx_cases", points=points)
        client.upsert(collection_name="crime_cases", points=points)
        print(f"Upserted {i + len(batch)}/{len(cases)} vectors...")

    print("Qdrant insertion complete.")

def main():
    print("--- Starting 1000 Indian Scenarios Seeding Process ---")
    db_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(db_url)
    
    seed_lookup_tables(conn)
    officer_id = get_officer_id(conn)
    data = generate_data(officer_id)
    
    insert_postgres(conn, data)
    insert_neo4j(data)
    insert_qdrant(data)
    
    conn.close()
    print("--- Successfully seeded 1000 cases with NO null values across all databases! ---")

if __name__ == "__main__":
    main()
