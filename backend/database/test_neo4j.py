import os
import sys
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load the .env file from the same directory
load_dotenv()

def test_neo4j_connection():
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")
    
    if not uri or not password:
        print("[FAIL] NEO4J_URI or NEO4J_PASSWORD not found in .env file.")
        sys.exit(1)
        
    print(f"Attempting to connect to Neo4j at: {uri}...")
    
    try:
        # Connect to the cloud instance
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # This will throw an exception if credentials or network is bad
        driver.verify_connectivity()
        print("[SUCCESS] Connected to Neo4j Aura Graph Database!")
        
        # Execute a small test query to get the database version
        records, _, _ = driver.execute_query("CALL dbms.components() YIELD versions RETURN versions[0] AS version")
        if records:
            print(f"[INFO] Database Version: Neo4j {records[0]['version']}")
            
        driver.close()
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")

if __name__ == "__main__":
    test_neo4j_connection()
