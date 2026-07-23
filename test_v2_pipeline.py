import asyncio
# pyrefly: ignore [missing-import]
import httpx
import json

# Configure endpoints
AI_ENGINE_URL = "http://127.0.0.1:8001/ai/v2/ask"
# IMPORTANT: Replace with a valid JWT token from your Django login if endpoints require auth
AUTH_TOKEN = "" 

TEST_QUERIES = [
    {
        "id": "Q1",
        "type": "suspect_query",
        "question": "Who are the accused suspects in case FIR-2026-10005?",
    },
    {
        "id": "Q2",
        "type": "case_lookup",
        "question": "Give me the summary and status of case FIR-2026-10150.",
    },
    {
        "id": "Q3",
        "type": "criminal_network",
        "question": "Show me the criminal network connections for FIR-2026-12000.",
    },
    {
        "id": "Q4",
        "type": "victim_query",
        "question": "Who filed the complaint for FIR-2026-13000?",
    },
    {
        "id": "Q5",
        "type": "fuzzy_search",
        "question": "Are there any recent cases involving vehicle theft?",
    },
    {
        "id": "Q6",
        "type": "fuzzy_search",
        "question": "Summarize cases involving cyber fraud.",
    },
    {
        "id": "Q7",
        "type": "case_lookup",
        "question": "What is the sequence of events and timeline for FIR-2026-11500?",
    },
    {
        "id": "Q8",
        "type": "multi_hop_complex",
        "question": "Find the case details for FIR-2026-14500 and list all persons involved.",
    },
    {
        "id": "Q9",
        "type": "fuzzy_search",
        "question": "Find incidents of kidnapping or extortion.",
    },
    {
        "id": "Q10",
        "type": "edge_case_no_data",
        "question": "Show me the details of FIR-9999-XYZ which does not exist.",
    }
]

async def run_test(client: httpx.AsyncClient, query: dict) -> dict:
    payload = {
        "user_id": "TEST-USER-V2",
        "session_id": f"TEST-SESSION-{query['id']}",
        "question": query["question"]
    }
    
    headers = {"Content-Type": "application/json"}
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"

    print(f"\n[{query['id']}] Sending query: {query['question']}")
    
    try:
        response = await client.post(AI_ENGINE_URL, json=payload, headers=headers, timeout=30.0)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "id": query["id"],
                "status": "SUCCESS",
                "intent": data.get("intent"),
                "clarification_needed": data.get("clarification_needed"),
                "clarification_question": data.get("clarification_question"),
                "evidence_count": data.get("evidence_bundle", {}).get("evidence_count", 0) if data.get("evidence_bundle") else 0,
                "confidence_label": data.get("confidence_label"),
                "critic_passed": data.get("critic_passed"),
                "finding_1": data.get("key_findings", [{}])[0].get("finding") if data.get("key_findings") else None
            }
        else:
            return {
                "id": query["id"],
                "status": "HTTP_ERROR",
                "code": response.status_code,
                "detail": response.text
            }
    except Exception as e:
        return {
            "id": query["id"],
            "status": "EXCEPTION",
            "detail": str(e)
        }

async def main():
    print("==================================================")
    print("  VigilX V2 Pipeline Dedicated Testing Script")
    print("==================================================")
    print(f"Targeting: {AI_ENGINE_URL}")
    print(f"Auth Token Provided: {'Yes' if AUTH_TOKEN else 'No (API must allow unauthenticated testing)'}")
    print("--------------------------------------------------")
    
    results = []
    async with httpx.AsyncClient() as client:
        for q in TEST_QUERIES:
            res = await run_test(client, q)
            results.append(res)
            
            # Print intermediate result
            if res.get("status") == "EXCEPTION":
                print(f"  -> ERROR: {res.get('detail')}")
            else:
                print(f"  -> Intent: {res.get('intent', 'N/A')}")
                print(f"  -> Evidence Count: {res.get('evidence_count', 0)}")
                print(f"  -> Confidence: {res.get('confidence_label', 'N/A')}")
                if res.get('clarification_needed'):
                    print(f"  -> Clarification Requested: {res.get('clarification_question')}")
                if res.get('finding_1'):
                    print(f"  -> Top Finding: {res.get('finding_1')}")
            
    print("\n==================================================")
    print("                 FINAL TEST SUMMARY               ")
    print("==================================================")
    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    with_evidence = sum(1 for r in results if r.get("evidence_count", 0) > 0)
    
    print(f"Total Tests Run: {len(TEST_QUERIES)}")
    print(f"Successful HTTP 200: {success_count}/{len(TEST_QUERIES)}")
    print(f"Queries that fetched Evidence > 0: {with_evidence}/{len(TEST_QUERIES)}")
    print("\nIf Evidence Count is 0 across the board, check:")
    print("  1. Is the Django API Server running on port 8000/8001?")
    print("  2. Did you provide a valid JWT AUTH_TOKEN at the top of this script?")
    print("  3. Are the databases (PostgreSQL, Neo4j, Qdrant) seeded with mock data?")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
