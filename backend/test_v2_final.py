"""
V2 Comprehensive Verification Test - Fixed
Tests the ai/v2/ask endpoint with Easy, Medium, and Hard questions.
Uses correct V2 InvestigationResponse schema fields.
"""
import requests
import json
import time
import sys

AI_ENGINE_URL = "http://127.0.0.1:8001"
DJANGO_URL = "http://127.0.0.1:8000"

TEST_CASES = [
    {
        "id": "EASY-1",
        "difficulty": "Easy",
        "question": "What is the current status of FIR-IN-2026-0001?",
        "expected_keywords": ["UNDER_INVESTIGATION", "under investigation"],
        "description": "Simple status lookup for a known FIR"
    },
    {
        "id": "EASY-2",
        "difficulty": "Easy",
        "question": "What type of crime was reported in FIR-IN-2026-0001?",
        "expected_keywords": ["BURGLARY", "burglary"],
        "description": "Simple crime type lookup"
    },
    {
        "id": "MEDIUM-1",
        "difficulty": "Medium",
        "question": "Who are the accused in FIR-IN-2026-0001 and what sections are applied to them?",
        "expected_keywords": ["accused", "section", "IPC", "BNS"],
        "description": "Multi-entity query requiring accused + legal sections"
    },
    {
        "id": "MEDIUM-2",
        "difficulty": "Medium",
        "question": "How many FIR cases have the status UNDER_INVESTIGATION?",
        "expected_keywords": ["cases", "under_investigation", "UNDER_INVESTIGATION"],
        "description": "Aggregation query on case status"
    },
    {
        "id": "HARD-1",
        "difficulty": "Hard",
        "question": "List the top 5 crime types by number of cases reported and show the count for each.",
        "expected_keywords": ["BURGLARY", "THEFT", "MURDER", "ROBBERY", "ASSAULT", "KIDNAPPING", "FRAUD", "count", "cases"],
        "description": "Complex aggregation requiring grouping and sorting"
    },
]


def call_v2(question, session_id):
    """Call the V2 ask endpoint"""
    url = f"{AI_ENGINE_URL}/ai/v2/ask"
    payload = {
        "question": question,
        "session_id": session_id,
        "user_id": "TEST-USER-V2"
    }
    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        return resp.status_code, resp.json()
    except requests.exceptions.Timeout:
        return 408, {"error": "Request timed out after 120s"}
    except Exception as e:
        return 500, {"error": str(e)}


def extract_answer_text(response_data):
    """Extract all text content from V2 InvestigationResponse"""
    parts = []
    
    # executive_summary is the main answer
    summary = response_data.get("executive_summary", "")
    if summary:
        parts.append(summary)
    
    # key_findings contain detailed findings
    for finding in response_data.get("key_findings", []):
        if isinstance(finding, dict):
            parts.append(finding.get("finding", ""))
        elif isinstance(finding, str):
            parts.append(finding)
    
    # clarification_question for fallback
    cq = response_data.get("clarification_question", "")
    if cq:
        parts.append(cq)
    
    # evidence_bundle text
    bundle = response_data.get("evidence_bundle")
    if bundle and isinstance(bundle, dict):
        top_text = bundle.get("top_evidence_text", "")
        if top_text:
            parts.append(top_text)
    
    return "\n".join(parts)


def check_answer(answer_text, expected_keywords):
    """Check if the answer contains expected keywords"""
    answer_lower = answer_text.lower()
    
    found = []
    missing = []
    for kw in expected_keywords:
        if kw.lower() in answer_lower:
            found.append(kw)
        else:
            missing.append(kw)
    
    passed = len(found) >= 1
    return passed, found, missing


def main():
    print("=" * 80)
    print("  VigilX V2 Comprehensive Verification Test (Fixed)")
    print("=" * 80)
    print()

    # Pre-flight checks
    print("[PRE-FLIGHT] Checking services...")
    try:
        r = requests.get(f"{AI_ENGINE_URL}/health", timeout=5)
        print(f"  AI Engine: {r.json()}")
    except Exception as e:
        print(f"  AI Engine: FAILED - {e}")
        sys.exit(1)

    try:
        r = requests.get(f"{DJANGO_URL}/api/cases/?fir_id=FIR-IN-2026-0001", timeout=5)
        data = r.json()
        print(f"  Django API: OK (FIR-IN-2026-0001 found: {data['count'] > 0})")
    except Exception as e:
        print(f"  Django API: FAILED - {e}")
        sys.exit(1)

    print()
    print("-" * 80)

    results = []
    
    for i, tc in enumerate(TEST_CASES):
        session_id = f"TEST-{tc['id']}-{int(time.time())}"
        print(f"\n[{tc['id']}] {tc['difficulty']} | {tc['description']}")
        print(f"  Q: {tc['question']}")
        
        status_code, response_data = call_v2(tc["question"], session_id)
        
        print(f"  HTTP: {status_code}")
        
        if status_code != 200:
            print(f"  RESULT: FAIL (HTTP {status_code})")
            print(f"  Error: {response_data.get('error', response_data)}")
            results.append({**tc, "status": "FAIL", "reason": f"HTTP {status_code}", "answer_text": ""})
        else:
            answer_text = extract_answer_text(response_data)
            confidence = response_data.get("confidence", 0)
            confidence_label = response_data.get("confidence_label", "unknown")
            intent = response_data.get("intent", "unknown")
            clarification = response_data.get("clarification_needed", False)
            
            # Count evidence
            bundle = response_data.get("evidence_bundle")
            evidence_count = 0
            if bundle and isinstance(bundle, dict):
                evidence_count = bundle.get("evidence_count", 0)
            
            print(f"  Intent: {intent} | Confidence: {confidence_label} ({confidence:.2f}) | Evidence: {evidence_count}")
            print(f"  Clarification needed: {clarification}")
            
            # Show answer preview
            preview = answer_text[:300].replace('\n', ' | ')
            print(f"  Answer: {preview}...")
            
            passed, found_kw, missing_kw = check_answer(answer_text, tc["expected_keywords"])
            
            if passed:
                print(f"  RESULT: PASS (matched: {found_kw})")
            else:
                print(f"  RESULT: FAIL (no keywords matched. Missing: {missing_kw})")
            
            results.append({
                **tc,
                "status": "PASS" if passed else "FAIL",
                "confidence": confidence,
                "confidence_label": confidence_label,
                "evidence_count": evidence_count,
                "intent": intent,
                "found_keywords": found_kw,
                "missing_keywords": missing_kw,
                "answer_text": answer_text[:500],
                "clarification": clarification,
            })
        
        # Delay between requests to avoid rate limiting
        if i < len(TEST_CASES) - 1:
            print("  (waiting 8s to avoid rate limits...)")
            time.sleep(8)

    # Summary
    print("\n" + "=" * 80)
    print("  TEST SUMMARY")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    
    print(f"\n  Total: {total} | Passed: {passed} | Failed: {failed} | Pass Rate: {passed/total*100:.0f}%\n")
    
    for r in results:
        icon = "PASS" if r["status"] == "PASS" else "FAIL"
        conf = r.get("confidence_label", "N/A")
        ev = r.get("evidence_count", "N/A")
        print(f"  [{icon}] {r['id']:10} | {r['difficulty']:6} | conf={conf} ev={ev} | {r['description']}")
    
    print("\n" + "=" * 80)
    
    # Detailed failure analysis
    failures = [r for r in results if r["status"] == "FAIL"]
    if failures:
        print("\n  FAILURE DETAILS:")
        for f in failures:
            print(f"\n  [{f['id']}] {f['question']}")
            print(f"    Reason: {f.get('reason', 'Keywords not found')}")
            print(f"    Missing: {f.get('missing_keywords', 'N/A')}")
            print(f"    Answer preview: {f.get('answer_text', 'N/A')[:300]}")
    else:
        print("\n  ALL TESTS PASSED!")
    
    print()
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
