import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

AI_ENGINE_URL = "http://127.0.0.1:8001/ai/v2/ask"
AUTH_TOKEN = os.getenv("AI_ENGINE_DOWNSTREAM_SERVICE_TOKEN", "vigilx-internal-service-token-999")

TEST_QUERIES = [
    {
        "id": "EASY",
        "question": "What is the status of case FIR-IN-2026-0001?",
    },
    {
        "id": "MEDIUM",
        "question": "Who are the accused in FIR-IN-2026-0001 and what sections are applied to them?",
    },
    {
        "id": "HARD",
        "question": "Find the criminal network connections for Siddharth Lala, and list any cases or bank transactions associated with him.",
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
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}" # Fix: ServiceTokenAuthentication expects 'Bearer' prefix

    print(f"\n[{query['id']}] Sending query: {query['question']}")
    
    try:
        response = await client.post(AI_ENGINE_URL, json=payload, headers=headers, timeout=120.0)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "id": query["id"],
                "status": "SUCCESS",
                "intent": data.get("intent"),
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
    print("  VigilX V2 Pipeline Custom Testing Script")
    print("==================================================")
    print(f"Targeting: {AI_ENGINE_URL}")
    print("--------------------------------------------------")
    
    results = []
    async with httpx.AsyncClient() as client:
        for q in TEST_QUERIES:
            res = await run_test(client, q)
            results.append(res)
            
            # Print intermediate result
            if res.get("status") == "EXCEPTION":
                print(f"  -> ERROR: {res.get('detail')}")
            elif res.get("status") == "HTTP_ERROR":
                print(f"  -> HTTP ERROR {res.get('code')}: {res.get('detail')}")
            else:
                print(f"  -> Intent: {res.get('intent', 'N/A')}")
                print(f"  -> Evidence Count: {res.get('evidence_count', 0)}")
                print(f"  -> Confidence: {res.get('confidence_label', 'N/A')}")
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
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())
