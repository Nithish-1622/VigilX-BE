import os
import sys
from dotenv import load_dotenv
import psycopg2
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from fastembed import TextEmbedding

# Load the .env file from the root directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

def seed_postgres():
    print("\n--- 1. Seeding PostgreSQL (Relational) ---")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Missing DATABASE_URL. Skipping Postgres.")
        return
        
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # Run Schema to ensure tables exist
    schema_path = os.path.join(os.path.dirname(__file__), 'postgres', 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    print("Executing schema.sql to ensure tables exist in cloud...")
    try:
        cur.execute(schema_sql)
        conn.commit()
    except Exception as e:
        print(f"Schema issue (tables might already exist): {e}")
        conn.rollback()

    print("Inserting mock data...")
    # Add dummy case
    # Note: We aren't using ON CONFLICT DO NOTHING because it requires a unique constraint on ID in Postgres, 
    # but the schema already defines PRIMARY KEYs so we just catch the IntegrityError if it already exists.
    try:
        cur.execute("INSERT INTO CaseMaster (CaseMasterID, CaseNo, BriefFacts) VALUES (101, 'FIR-2026-101', 'Bank robbery at downtown branch by three masked suspects.')")
        cur.execute("INSERT INTO ComplainantDetails (ComplainantID, CaseMasterID, ComplainantName, AgeYear) VALUES (201, 101, 'Jane Smith', 45)")
        cur.execute("INSERT INTO Accused (AccusedMasterID, CaseMasterID, AccusedName, AgeYear) VALUES (301, 101, 'John The Shadow Doe', 42)")
        conn.commit()
        print("PostgreSQL seeded successfully!")
    except psycopg2.IntegrityError:
        print("Data already exists in Postgres. Skipping insert.")
        conn.rollback()
        
    cur.close()
    conn.close()

def seed_neo4j():
    print("\n--- 2. Seeding Neo4j (Graph) ---")
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    
    if not uri:
        print("Missing NEO4J_URI. Skipping Neo4j.")
        return
        
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    cypher = """
    MERGE (c:Case {id: 'CASE_101'})
    SET c.case_number = 'FIR-2026-101', c.status = 'OPEN'
    
    MERGE (comp:Person {id: 'COMP_201'})
    SET comp.name = 'Jane Smith', comp.age_group = '45'
    
    MERGE (acc:Person {id: 'ACC_301'})
    SET acc.name = 'John The Shadow Doe', acc.age_group = '42'
    
    MERGE (comp)-[:FILED_BY]->(c)
    MERGE (acc)-[:ACCUSED_IN]->(c)
    """
    driver.execute_query(cypher)
    print("Neo4j Graph nodes and relationships created successfully!")
    driver.close()

def seed_qdrant():
    print("\n--- 3. Seeding Qdrant (Vector) ---")
    host = os.getenv("QDRANT_HOST")
    api_key = os.getenv("QDRANT_API_KEY")
    
    if not host:
        print("Missing QDRANT_HOST. Skipping Qdrant.")
        return
        
    client = QdrantClient(url=host, api_key=api_key)
    
    # Ensure collection exists
    try:
        client.create_collection(
            collection_name="cases",
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print("Created 'cases' collection.")
    except Exception as e:
        print("'cases' collection already exists.")
        
    print("Generating embeddings locally using fastembed...")
    # Fastembed generates 384 dim vectors by default for BGE-small
    embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    
    text = "Bank robbery at downtown branch by three masked suspects."
    vector = list(embedding_model.embed([text]))[0].tolist()
    
    print("Uploading vector to Qdrant...")
    client.upsert(
        collection_name="cases",
        points=[
            PointStruct(
                id=101,
                vector=vector,
                payload={"case_id": "CASE_101", "brief_facts": text}
            )
        ]
    )
    print("Vector DB seeded successfully!")

if __name__ == "__main__":
    print("Starting Multi-DB Seeding Process...")
    seed_postgres()
    seed_neo4j()
    seed_qdrant()
    print("\nALL DATABASES SUCCESSFULLY SEEDED WITH MOCK DATA!")
