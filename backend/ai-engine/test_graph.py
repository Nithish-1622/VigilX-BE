import asyncio
import httpx
from fastapi.testclient import TestClient
from main import app

# Simple test to verify the endpoints are registered and returning proper JSON structures
client = TestClient(app)

def test_graph_endpoints():
    print("Testing Graph Visualization API...")
    res = client.get("/ai/graph/visualize")
    print(f"Status: {res.status_code}")
    assert res.status_code == 200
    print(res.json())

    print("\nTesting Community Detection API...")
    res = client.get("/ai/graph/community")
    print(f"Status: {res.status_code}")
    assert res.status_code == 200
    print(res.json())

    print("\nTesting Role & Centrality API...")
    res = client.get("/ai/graph/centrality")
    print(f"Status: {res.status_code}")
    assert res.status_code == 200
    print(res.json())

    print("\nTesting Shortest Path API...")
    res = client.get("/ai/graph/shortest-path?source_id=1&target_id=2")
    print(f"Status: {res.status_code}")
    assert res.status_code == 200
    print(res.json())

    print("\nTesting Geographic Mapping API (3.7)...")
    res = client.get("/ai/graph/geography")
    print(f"Status: {res.status_code}")
    assert res.status_code == 200
    
    print("\nTesting Temporal Dynamics API (3.8)...")
    res = client.get("/ai/graph/temporal?year=2024")
    print(f"Status: {res.status_code}")
    assert res.status_code == 200
    
    print("\nTesting Hidden Link Discovery API (3.9)...")
    res = client.get("/ai/graph/hidden-links?suspect_id=1")
    print(f"Status: {res.status_code}")
    assert res.status_code == 200
    
    print("\nTesting Interactive Graph Query API (3.11)...")
    res = client.post("/ai/graph/query?cypher=MATCH%20(n)%20RETURN%20n%20LIMIT%201")
    print(f"Status: {res.status_code}")
    assert res.status_code == 200
    
    print("\nTesting Subgraph Export API (3.12)...")
    res = client.get("/ai/graph/export?fir_id=FIR123")
    print(f"Status: {res.status_code}")
    assert res.status_code == 200

if __name__ == "__main__":
    test_graph_endpoints()
    print("All Phase 3 Graph Endpoints successfully registered and responding!")
