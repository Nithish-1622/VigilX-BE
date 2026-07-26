import os
from dotenv import load_dotenv
import psycopg2
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from qdrant_client.models import Filter

# Load the .env file from the root directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

def clear_postgres():
    print("\n--- 1. Clearing PostgreSQL (Relational) ---")
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Missing DATABASE_URL. Skipping Postgres.")
        return
        
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    # We truncate the tables specifically related to application data.
    # CASCADE ensures any dependent rows in other tables (e.g. clue entities, bank accounts) are also removed.
    tables_to_truncate = [
        "casemaster",
        "victim",
        "complainantdetails",
        "accused",
        "cases_clueentity",
        "cases_bankaccount",
        "cases_transaction"
    ]
    
    print(f"Truncating application tables: {', '.join(tables_to_truncate)}...")
    try:
        cur.execute(f"TRUNCATE TABLE {', '.join(tables_to_truncate)} CASCADE;")
        conn.commit()
        print("PostgreSQL application data cleared successfully!")
    except Exception as e:
        print(f"Error clearing Postgres data: {e}")
        conn.rollback()
        
    cur.close()
    conn.close()

def clear_neo4j():
    print("\n--- 2. Clearing Neo4j (Graph) ---")
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    
    if not uri:
        print("Missing NEO4J_URI. Skipping Neo4j.")
        return
        
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    cypher = "MATCH (n) DETACH DELETE n;"
    print("Deleting all nodes and relationships...")
    try:
        driver.execute_query(cypher)
        print("Neo4j Graph data cleared successfully!")
    except Exception as e:
        print(f"Error clearing Neo4j data: {e}")
    finally:
        driver.close()

def clear_qdrant():
    print("\n--- 3. Clearing Qdrant (Vector) ---")
    host = os.getenv("QDRANT_HOST")
    api_key = os.getenv("QDRANT_API_KEY")
    
    if not host:
        print("Missing QDRANT_HOST. Skipping Qdrant.")
        return
        
    client = QdrantClient(url=host, api_key=api_key)
    
    collections = client.get_collections().collections
    if not collections:
        print("No collections found in Qdrant.")
        return
        
    for collection in collections:
        print(f"Emptying collection: '{collection.name}'...")
        try:
            client.delete(
                collection_name=collection.name,
                points_selector=Filter() # Empty filter deletes all points
            )
            print(f"Cleared points from '{collection.name}'.")
        except Exception as e:
            print(f"Error clearing collection '{collection.name}': {e}")
            
    print("Vector DB points cleared successfully!")

if __name__ == "__main__":
    print("Starting Data Clearing Process...")
    clear_postgres()
    clear_neo4j()
    clear_qdrant()
    print("\nALL SPECIFIED DATABASES SUCCESSFULLY CLEARED OF APPLICATION DATA!\n")
