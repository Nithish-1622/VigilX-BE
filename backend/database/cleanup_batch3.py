import os
import psycopg2
from neo4j import GraphDatabase
# pyrefly: ignore [missing-import]
from qdrant_client import QdrantClient
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

PG_URL = os.getenv("DATABASE_URL")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = os.getenv("QDRANT_PORT")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

THRESHOLD_ID = 15000  # Start of Batch 3 (if start-id was 10000 and batch-size 2500)

def cleanup_postgres():
    print("Cleaning up Postgres (Cases >= 15000)...")
    try:
        conn = psycopg2.connect(PG_URL)
        cur = conn.cursor()
        
        cur.execute("DELETE FROM Accused WHERE CaseMasterID >= %s", (THRESHOLD_ID,))
        cur.execute("DELETE FROM ComplainantDetails WHERE CaseMasterID >= %s", (THRESHOLD_ID,))
        cur.execute("DELETE FROM CaseMaster WHERE CaseMasterID >= %s", (THRESHOLD_ID,))
        
        conn.commit()
        print(f"Deleted {cur.rowcount} CaseMaster records (plus related tables) from Postgres.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Postgres cleanup error: {e}")

def cleanup_neo4j():
    print("Cleaning up Neo4j (Cases >= 15000)...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            # Delete Accused relationships and nodes
            session.run("""
                MATCH (p:Person)-[r:ACCUSED_IN]->(c:Case)
                WHERE toInteger(split(c.case_id, '-')[1]) >= $thresh
                DELETE r, p
            """, thresh=THRESHOLD_ID)
            
            # Delete Complainant relationships and nodes
            session.run("""
                MATCH (p:Person)-[r:FILED_BY]->(c:Case)
                WHERE toInteger(split(c.case_id, '-')[1]) >= $thresh
                DELETE r, p
            """, thresh=THRESHOLD_ID)
            
            # Delete Case nodes
            res = session.run("""
                MATCH (c:Case)
                WHERE toInteger(split(c.case_id, '-')[1]) >= $thresh
                DELETE c
                RETURN count(c) as deleted_count
            """, thresh=THRESHOLD_ID)
            count = res.single()['deleted_count']
            print(f"Deleted {count} Case nodes from Neo4j.")
        driver.close()
    except Exception as e:
        print(f"Neo4j cleanup error: {e}")

def cleanup_qdrant():
    print("Cleaning up Qdrant (Cases >= 15000)...")
    try:
        # pyrefly: ignore [missing-import]
        from qdrant_client.http.models import Filter, FieldCondition, Range
        qdrant = QdrantClient(url=f"{QDRANT_HOST}:{QDRANT_PORT}", api_key=QDRANT_API_KEY)
        
        # Qdrant delete by ID condition
        # Points in bulk_seeder have integer ID = CaseMasterID
        # Qdrant client delete method allows deleting a list of IDs.
        # However, getting all IDs >= 15000 is tricky. Instead we can delete using a Filter if ID was in payload, but ID is the actual point ID.
        # Let's delete points by ID directly up to 20000 just to be safe.
        ids_to_delete = list(range(15000, 20000))
        qdrant.delete(
            collection_name="vigilx_cases",
            points_selector=ids_to_delete
        )
        print("Deleted points >= 15000 from Qdrant.")
    except Exception as e:
        print(f"Qdrant cleanup error: {e}")

if __name__ == "__main__":
    cleanup_postgres()
    cleanup_neo4j()
    cleanup_qdrant()
    print("Cleanup Complete!")
