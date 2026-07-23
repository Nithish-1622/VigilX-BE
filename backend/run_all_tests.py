import os
# pyrefly: ignore [missing-import]
import django
import sys

# Setup Django to create a user and token
sys.path.append(os.path.join(os.path.dirname(__file__), 'django-api'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# pyrefly: ignore [missing-import]
from django.contrib.auth import get_user_model
# pyrefly: ignore [missing-import]
from rest_framework_simplejwt.tokens import RefreshToken
import requests
import time

User = get_user_model()

def run_tests():
    print("========================================")
    print("VIGILX END-TO-END AUTOMATED TEST SUITE")
    print("========================================")

    # 1. Create a test user and generate JWT
    print("\n[INIT] Generating Authentication Credentials...")
    user, created = User.objects.get_or_create(username='test_admin', defaults={'is_superuser': True, 'is_staff': True})
    if created:
        user.set_password('testpass123')
        user.save()
    
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    headers = {"Authorization": f"Bearer {token}"}
    print("[SUCCESS] JWT Token generated successfully.")

    django_base = "http://127.0.0.1:8000/api"
    fastapi_base = "http://127.0.0.1:8001"
    
    passed = 0
    failed = 0
    
    def hit_endpoint(name, url, method="GET", payload=None):
        nonlocal passed, failed
        try:
            if method == "GET":
                res = requests.get(url, headers=headers, timeout=5)
            else:
                res = requests.post(url, headers=headers, json=payload, timeout=5)
                
            if res.status_code in [200, 201]:
                print(f"[PASS] {name} -> {res.status_code}")
                passed += 1
            else:
                print(f"[FAIL] {name} -> Expected 200, got {res.status_code}. Response: {res.text[:100]}")
                failed += 1
        except Exception as e:
            print(f"[ERROR] {name} -> Connection failed: {e}")
            failed += 1

    # PHASE 4: Analytics
    print("\n--- PHASE 4: Crime Pattern & Trend Analytics ---")
    hit_endpoint("4.1 Spatio-Temporal Trends", f"{django_base}/analytics/trends/")
    hit_endpoint("4.2 Seasonal Analytics", f"{django_base}/analytics/seasonal/")
    hit_endpoint("4.3 Modus Operandi Analysis", f"{django_base}/analytics/mo/")
    hit_endpoint("4.4 Comparative Dashboard", f"{django_base}/analytics/compare/")
    hit_endpoint("4.7 GIS Integration", f"{django_base}/analytics/gis/")
    hit_endpoint("4.9 Pattern Mining", f"{django_base}/analytics/patterns/")

    # PHASE 5: Socio-Demographics
    print("\n--- PHASE 5: Socio-Demographic Impacts ---")
    hit_endpoint("5.1 Demographic Breakdown", f"{django_base}/analytics/demographics/")
    hit_endpoint("5.6 Public Safety Index", f"{django_base}/analytics/safety-index/")

    # PHASE 6: Profiling
    print("\n--- PHASE 6: Predictive Profiling ---")
    hit_endpoint("6.1 Repeat Offender ID", f"{django_base}/profiling/repeat-offenders/1/")
    hit_endpoint("6.2 Behavioral Clustering", f"{django_base}/profiling/behavioral-clusters/")
    hit_endpoint("6.4 Predictive Recidivism", f"{django_base}/profiling/recidivism/1/")

    # PHASE 7: Decision Support
    print("\n--- PHASE 7: Investigator Decision Support ---")
    hit_endpoint("7.1 AI Case Summary", f"{django_base}/cases/FIR-2026-001/ai-summary/")
    hit_endpoint("7.2 Case Timeline", f"{django_base}/cases/FIR-2026-001/timeline/")
    hit_endpoint("7.4 Recommended Leads", f"{django_base}/cases/FIR-2026-001/leads/")
    hit_endpoint("7.10 Supervisor Analytics", f"{django_base}/supervisor/analytics/")

    # PHASE 8: Financial Crime
    print("\n--- PHASE 8: Financial Link Analysis ---")
    hit_endpoint("8.1 Transaction Network", f"{django_base}/finance/network/AC-778-999-1/")
    hit_endpoint("8.2 Suspicious Transactions", f"{django_base}/finance/suspicious/")
    hit_endpoint("8.8 Fraud Patterns", f"{django_base}/finance/fraud-patterns/")

    # PHASE 9: Forecasting
    print("\n--- PHASE 9: Forecasting & Early Warning ---")
    hit_endpoint("9.1 Hotspot Prediction", f"{django_base}/forecasting/hotspots/")
    hit_endpoint("9.3 Trend Extrapolation", f"{django_base}/forecasting/trends/")
    hit_endpoint("9.4 Early Warning Alerts", f"{django_base}/forecasting/warnings/")

    # PHASE 10: Explainable AI
    print("\n--- PHASE 10: Explainable AI (XAI) ---")
    hit_endpoint("10.2 Reasoning Viz", f"{django_base}/xai/reasoning/Q-123/")
    hit_endpoint("10.6 Model Transparency", f"{django_base}/xai/transparency/")
    hit_endpoint("10.7 Explainable Risk", f"{django_base}/xai/explain-risk/1/")

    # FASTAPI AI ENGINE TESTS
    print("\n--- AI ENGINE ENDPOINTS (FastAPI) ---")
    hit_endpoint("AI Engine Root", f"{fastapi_base}/")
    hit_endpoint("AI Health Check", f"{fastapi_base}/health")
    hit_endpoint("3.12 Subgraph Export", f"{fastapi_base}/ai/graph/export?fir_id=FIR-2026-001")

    print("\n========================================")
    print(f"TEST RUN COMPLETE: {passed} Passed | {failed} Failed")
    print("========================================")
    
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
