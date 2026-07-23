import os
import argparse
import time
import random
from datetime import datetime, timedelta
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from faker import Faker
import psycopg2
# pyrefly: ignore [missing-import]
from psycopg2.extras import execute_values
# pyrefly: ignore [missing-import]
from neo4j import GraphDatabase
# pyrefly: ignore [missing-import]
from qdrant_client import QdrantClient
# pyrefly: ignore [missing-import]
from qdrant_client.models import PointStruct, VectorParams, Distance
# pyrefly: ignore [missing-import]
from fastembed import TextEmbedding

# Load the .env file from the root directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

fake = Faker('en_IN')

# Setup Clients
PG_URL = os.getenv("DATABASE_URL")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = os.getenv("QDRANT_PORT")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

CRIME_CATEGORIES = [1, 2, 3, 4] # Assuming 1: Theft, 2: Assault, 3: Fraud, 4: Homicide
STATUSES = [1, 2, 3] # 1: Open, 2: Closed, 3: Pending Trial

def generate_cases_batch(start_id, count):
    cases = []
    complainants = []
    accused_list = []
    
    current_year = 2026
    
    for i in range(count):
        case_id = start_id + i
        case_no = f'FIR-{current_year}-{case_id}'
        # Random date in the past 2 years
        reg_date = fake.date_between(start_date='-2y', end_date='today')
        
        # Brief Facts
        offense = random.choice(["robbery", "assault", "cyber fraud", "kidnapping", "extortion", "vehicle theft"])
        location = fake.city()
        facts = f"Incident of {offense} reported in {location}. {fake.text(max_nb_chars=150)}"
        
        # (CaseMasterID, CrimeNo, CaseNo, CrimeRegisteredDate, BriefFacts, CaseCategoryID, CaseStatusID)
        cases.append((
            case_id, case_no, case_no, reg_date, facts, 
            random.choice(CRIME_CATEGORIES), random.choice(STATUSES)
        ))
        
        # Complainant
        comp_id = case_id * 10 + 1
        complainants.append((
            comp_id, case_id, fake.name(), random.randint(20, 70)
        ))
        
        # Accused (1 to 3 accused per case)
        num_accused = random.randint(1, 3)
        for j in range(num_accused):
            acc_id = case_id * 10 + 2 + j
            accused_list.append((
                acc_id, case_id, fake.name(), random.randint(18, 65)
            ))
            
    return cases, complainants, accused_list

def seed_postgres(cases, complainants, accused_list):
    conn = psycopg2.connect(PG_URL)
    cur = conn.cursor()
    
    # Pre-seed lookup tables to satisfy Foreign Keys
    print("Postgres: Ensuring lookup tables have data...")
    cur.execute("INSERT INTO CaseCategory (CaseCategoryID, LookupValue) VALUES (1, 'Theft'), (2, 'Assault'), (3, 'Fraud'), (4, 'Homicide') ON CONFLICT (CaseCategoryID) DO NOTHING")
    cur.execute("INSERT INTO CaseStatusMaster (CaseStatusID, CaseStatusName) VALUES (1, 'Open'), (2, 'Closed'), (3, 'Pending Trial') ON CONFLICT (CaseStatusID) DO NOTHING")
    
    print(f"Postgres: Inserting {len(cases)} Cases...")
    execute_values(cur, """
        INSERT INTO CaseMaster (CaseMasterID, CrimeNo, CaseNo, CrimeRegisteredDate, BriefFacts, CaseCategoryID, CaseStatusID) 
        VALUES %s ON CONFLICT (CaseMasterID) DO NOTHING
    """, cases)
    
    print(f"Postgres: Inserting {len(complainants)} Complainants...")
    execute_values(cur, """
        INSERT INTO ComplainantDetails (ComplainantID, CaseMasterID, ComplainantName, AgeYear) 
        VALUES %s ON CONFLICT (ComplainantID) DO NOTHING
    """, complainants)
    
    print(f"Postgres: Inserting {len(accused_list)} Accused...")
    execute_values(cur, """
        INSERT INTO Accused (AccusedMasterID, CaseMasterID, AccusedName, AgeYear) 
        VALUES %s ON CONFLICT (AccusedMasterID) DO NOTHING
    """, accused_list)
    
    conn.commit()
    cur.close()
    conn.close()

def seed_neo4j(cases, complainants, accused_list):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    print(f"Neo4j: Preparing UNWIND payload for {len(cases)} cases...")
    
    with driver.session() as session:
        # 1. Create Cases
        case_data = [{"case_id": f"FIR-{c[0]}", "case_no": c[2]} for c in cases]
        session.run("""
            UNWIND $cases AS c
            MERGE (case:Case {case_id: c.case_id})
            SET case.case_no = c.case_no
        """, cases=case_data)
        
        # 2. Create Complainants & Links
        comp_data = [{"person_id": f"P-{c[0]}", "name": c[2], "case_id": f"FIR-{c[1]}"} for c in complainants]
        session.run("""
            UNWIND $comps AS c
            MERGE (p:Person {person_id: c.person_id})
            SET p.name = c.name, p.type = 'Complainant'
            WITH p, c
            MATCH (case:Case {case_id: c.case_id})
            MERGE (p)-[:FILED_BY]->(case)
        """, comps=comp_data)
        
        # 3. Create Accused & Links
        acc_data = [{"person_id": f"A-{a[0]}", "name": a[2], "case_id": f"FIR-{a[1]}"} for a in accused_list]
        session.run("""
            UNWIND $accs AS a
            MERGE (p:Person {person_id: a.person_id})
            SET p.name = a.name, p.type = 'Accused'
            WITH p, a
            MATCH (case:Case {case_id: a.case_id})
            MERGE (p)-[:ACCUSED_IN]->(case)
        """, accs=acc_data)
        
    driver.close()
    print("Neo4j: Nodes and Relationships created via UNWIND.")

def seed_qdrant(cases):
    print("Qdrant: Generating embeddings (this takes CPU time)...")
    qdrant = QdrantClient(
        url=f"{QDRANT_HOST}:{QDRANT_PORT}",
        api_key=QDRANT_API_KEY
    )
    embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    collection_name = "vigilx_cases"
    
    # Try creating collection if doesn't exist
    try:
        qdrant.get_collection(collection_name)
    except:
        qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
    
    docs = [c[4] for c in cases] # BriefFacts
    embeddings = list(embedding_model.embed(docs))
    
    points = []
    for idx, case in enumerate(cases):
        points.append(PointStruct(
            id=case[0], # CaseMasterID
            vector=embeddings[idx].tolist(),
            payload={
                "case_no": case[2],
                "brief_facts": case[4]
            }
        ))
        
    print(f"Qdrant: Uploading {len(points)} vectors...")
    qdrant.upload_points(
        collection_name=collection_name,
        points=points
    )
    print("Qdrant: Upload complete.")

def main():
    parser = argparse.ArgumentParser(description="Bulk Data Seeder for VigilX")
    parser.add_argument('--cases', type=int, default=1000, help='Number of cases to generate')
    parser.add_argument('--batch-size', type=int, default=5000, help='Batch size for database inserts')
    parser.add_argument('--start-id', type=int, default=1000, help='Starting ID for CaseMasterID to avoid primary key collisions')
    args = parser.parse_args()
    
    total_cases = args.cases
    batch_size = args.batch_size
    start_id = args.start_id
    
    print(f"=== Starting Bulk Seeder: {total_cases} Cases ===")
    
    for i in range(0, total_cases, batch_size):
        chunk_size = min(batch_size, total_cases - i)
        current_start_id = start_id + i
        
        print(f"\n--- Processing Batch {i//batch_size + 1} ({chunk_size} records starting at ID {current_start_id}) ---")
        
        t0 = time.time()
        cases, complainants, accused = generate_cases_batch(current_start_id, chunk_size)
        print(f"Generation took {time.time()-t0:.2f}s")
        
        t1 = time.time()
        seed_postgres(cases, complainants, accused)
        print(f"Postgres Insert took {time.time()-t1:.2f}s")
        
        t2 = time.time()
        seed_neo4j(cases, complainants, accused)
        print(f"Neo4j Insert took {time.time()-t2:.2f}s")
        
        t3 = time.time()
        seed_qdrant(cases)
        print(f"Qdrant Insert & Embedding took {time.time()-t3:.2f}s")
        
    print("\n=== BULK SEEDING COMPLETE ===")

if __name__ == "__main__":
    main()
