# -*- coding: utf-8 -*-
"""
VigilX Pipeline Diagnostic - Tests each data source independently
to pinpoint where the evidence retrieval is failing.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import json
import requests
from dotenv import load_dotenv

# Load env from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

print("=" * 70)
print("VigilX Pipeline Diagnostic")
print("=" * 70)

# ============================================================
# 1. Test Django API directly (the REST gateway target)
# ============================================================
print("\n--- TEST 1: Django REST API (http://127.0.0.1:8000) ---")
DJANGO_BASE = "http://127.0.0.1:8000/api"

endpoints = [
    ("/cases/", "All cases"),
    ("/cases/?search=robbery", "Search: robbery"),
    ("/cases/?search=cyber", "Search: cyber"),
    ("/accused/", "All accused"),
    ("/accused/?search=Rajesh", "Search accused: Rajesh"),
    ("/accused/?search=Sanjay", "Search accused: Sanjay"),
    ("/victims/", "All victims"),
    ("/victims/?search=Anjali", "Search victim: Anjali"),
]

for path, desc in endpoints:
    try:
        headers = {"Authorization": f"Bearer {os.getenv('AI_ENGINE_DOWNSTREAM_SERVICE_TOKEN')}"}
        resp = requests.get(f"{DJANGO_BASE}{path}", headers=headers, timeout=5)
        data = resp.json()
        count = 0
        if isinstance(data, dict):
            if "results" in data:
                count = len(data["results"])
            elif "data" in data and isinstance(data["data"], dict):
                items = data["data"].get("items", data["data"].get("results", []))
                count = len(items) if isinstance(items, list) else 0
            elif "items" in data:
                count = len(data["items"])
        print(f"  [{resp.status_code}] {desc}: {count} items")
        if resp.status_code == 403 or resp.status_code == 401:
            print(f"    ** AUTH REQUIRED ** Response: {str(data)[:200]}")
        elif count == 0:
            print(f"    ** EMPTY RESULT ** Response: {str(data)[:200]}")
        elif count > 0:
            # Show first item
            if "results" in data:
                print(f"    First item: {str(data['results'][0])[:200]}")
    except Exception as e:
        print(f"  [ERR] {desc}: {e}")

# ============================================================
# 2. Test PostgreSQL directly (cloud Neon)
# ============================================================
print("\n--- TEST 2: PostgreSQL Cloud (Neon) ---")
try:
    import psycopg2
    db_url = os.getenv("DATABASE_URL")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    tables = [
        ("fir", "SELECT COUNT(*) FROM fir"),
        ("accused", "SELECT COUNT(*) FROM accused"),
        ("victim", "SELECT COUNT(*) FROM victim"),
        ("complainant", "SELECT COUNT(*) FROM complainant"),
    ]
    for name, sql in tables:
        try:
            cur.execute(sql)
            count = cur.fetchone()[0]
            print(f"  {name}: {count} rows")
            if count > 0:
                cur.execute(f"SELECT * FROM {name} LIMIT 1")
                row = cur.fetchone()
                cols = [desc[0] for desc in cur.description]
                print(f"    Columns: {cols}")
                print(f"    Sample: {dict(zip(cols, row))}")
        except Exception as e:
            print(f"  {name}: ERROR - {e}")
            conn.rollback()
    
    conn.close()
except Exception as e:
    print(f"  PostgreSQL connection failed: {e}")

# ============================================================
# 3. Test Neo4j (cloud Aura)
# ============================================================
print("\n--- TEST 3: Neo4j Cloud (Aura) ---")
try:
    from neo4j import GraphDatabase
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        # Count nodes
        result = session.run("MATCH (n) RETURN labels(n) AS label, count(n) AS cnt")
        for record in result:
            print(f"  Node type {record['label']}: {record['cnt']} nodes")
        
        # Check relationships
        result = session.run("MATCH ()-[r]->() RETURN type(r) AS rel_type, count(r) AS cnt")
        for record in result:
            print(f"  Relationship {record['rel_type']}: {record['cnt']}")
        
        # Check accused nodes specifically
        result = session.run("MATCH (a:Accused) RETURN a.name AS name LIMIT 5")
        names = [record["name"] for record in result]
        print(f"  Accused names: {names}")
    
    driver.close()
except Exception as e:
    print(f"  Neo4j connection failed: {e}")

# ============================================================
# 4. Test Qdrant (cloud)
# ============================================================
print("\n--- TEST 4: Qdrant Cloud ---")
try:
    from qdrant_client import QdrantClient
    
    qdrant_url = os.getenv("QDRANT_HOST")
    qdrant_key = os.getenv("QDRANT_API_KEY")
    
    client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
    collections = client.get_collections()
    print(f"  Collections: {[c.name for c in collections.collections]}")
    
    for coll in collections.collections:
        info = client.get_collection(coll.name)
        print(f"  Collection '{coll.name}': {info.points_count} points, dim={info.config.params.vectors.size}")
        
        # Scroll a few points to see payload
        points = client.scroll(collection_name=coll.name, limit=3)
        for pt in points[0]:
            print(f"    Point {pt.id}: payload={pt.payload}")
    
except Exception as e:
    print(f"  Qdrant connection failed: {e}")

# ============================================================
# 5. Test AI Engine /ai/ask with verbose logging
# ============================================================
print("\n--- TEST 5: AI Engine /ai/ask ---")
try:
    resp = requests.post("http://127.0.0.1:8001/ai/ask", json={
        "user_id": "diag-user",
        "session_id": "diag-session",
        "question": "Who is Rajesh Kumar"
    }, timeout=60)
    data = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Success: {data.get('success')}")
    print(f"  Answer: {data.get('data', {}).get('answer', 'N/A')[:200]}")
    print(f"  Evidence used: {data.get('data', {}).get('evidence_used', 0)}")
    
    meta = data.get("metadata", {})
    print(f"  Intent: {meta.get('intent')}")
    print(f"  RAG citations: {meta.get('rag_citations', 0)}")
    print(f"  SQL citations: {meta.get('sql_citations', 0)}")
    print(f"  Evidence sources: {meta.get('evidence_sources', 0)}")
    print(f"  Confidence: {meta.get('confidence')}")
    print(f"  Threshold met: {meta.get('evidence_threshold_met')}")
    print(f"  Query plan: {meta.get('query_plan', 'N/A')[:200]}")
    print(f"  Evidence breakdown: {meta.get('evidence_source_breakdown')}")
    
    citations = data.get("citations", [])
    print(f"  Total citations: {len(citations)}")
    for c in citations[:3]:
        print(f"    - source={c.get('source')}, snippet={str(c.get('snippet', ''))[:100]}")
        
except Exception as e:
    print(f"  AI Engine test failed: {e}")

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
