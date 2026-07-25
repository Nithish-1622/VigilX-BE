#!/usr/bin/env python3
"""
VigilX Catalyst Auth Test Script
===================================
Tests the full Catalyst Authentication flow by:
  1. Creating a test user via Catalyst REST API
  2. Verifying the user appears in our backend's DB via /api/auth/me/

Usage:
    python test_catalyst_auth.py --token <YOUR_ZOHO_OAUTH_TOKEN>

How to get your OAuth token:
    1. Go to: https://api-console.zoho.in/
    2. Click "Self Client" -> Generate Token
    3. Scope: ZohoCatalyst.projects.users.CREATE
    4. Copy the token and pass it with --token
"""

import argparse
import json
import sys
import requests

# ── Config ─────────────────────────────────────────────────────────────────────
PROJECT_ID = "50685000000013025"      # From .catalystrc
ORG_ID     = "60078718174"            # Development env ID from .catalystrc
DOMAIN     = "https://api.catalyst.zoho.in"  # India DC
BACKEND_URL = "https://vigilx.development.catalystappsail.in"

LOCAL_BACKEND_URL = "http://localhost:8000"

# Test user to create
TEST_USER = {
    "first_name": "Vigilx",
    "last_name": "TestUser",
    "email_id": f"testuser.vigilx@gmail.com",
    "platform_type": "web",
    "redirect_url": "https://vigilx.onslate.in"
}


def create_catalyst_user(oauth_token: str) -> dict:
    """Create a user in Catalyst's User Management via REST API."""
    url = f"{DOMAIN}/baas/v1/project/{PROJECT_ID}/project-user"
    headers = {
        "Authorization": f"Zoho-oauthtoken {oauth_token}",
        "CATALYST-ORG": ORG_ID,
        "Content-Type": "application/json",
    }
    payload = {
        "platform_type": "web",
        "user_details": {
            "first_name": TEST_USER["first_name"],
            "last_name": TEST_USER["last_name"],
            "email_id": TEST_USER["email_id"],
        },
        "redirect_url": TEST_USER["redirect_url"],
    }

    print(f"\n[1] Creating user in Catalyst: {TEST_USER['email_id']}")
    print(f"    URL: {url}")
    resp = requests.post(url, json=payload, headers=headers, timeout=15)

    if resp.status_code in (200, 201):
        data = resp.json()
        print(f"    ✅ User created! Catalyst response:")
        print(json.dumps(data, indent=4))
        return data
    else:
        print(f"    ❌ Failed to create user! HTTP {resp.status_code}")
        print(f"    Response: {resp.text}")
        sys.exit(1)


def check_providers():
    """Check the /api/auth/providers/ endpoint (public, no auth needed)."""
    url = f"{BACKEND_URL}/api/auth/providers/"
    print(f"\n[2] Checking provider list at: {url}")
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            print(f"    ✅ Providers endpoint OK!")
            print(json.dumps(resp.json(), indent=4))
        else:
            print(f"    ❌ HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"    ⚠️  Could not reach backend: {e}")
        print(f"    Make sure the backend is deployed and running at {BACKEND_URL}")


def list_catalyst_users(oauth_token: str):
    """List all users currently in the Catalyst project."""
    url = f"{DOMAIN}/baas/v1/project/{PROJECT_ID}/project-user"
    headers = {
        "Authorization": f"Zoho-oauthtoken {oauth_token}",
        "CATALYST-ORG": ORG_ID,
        "Content-Type": "application/json",
    }
    print(f"\n[3] Listing all users in Catalyst project '{PROJECT_ID}':")
    resp = requests.get(url, headers=headers, timeout=15)

    if resp.status_code == 200:
        data = resp.json()
        users = data.get("data", [])
        print(f"    ✅ Found {len(users)} user(s):")
        for u in users:
            print(f"      - {u.get('first_name')} {u.get('last_name')} <{u.get('email_id')}> | Role: {u.get('role_details', {}).get('role_name', 'N/A')}")
    else:
        print(f"    ❌ Failed to list users! HTTP {resp.status_code}")
        print(f"    Response: {resp.text}")


def main():
    parser = argparse.ArgumentParser(description="VigilX Catalyst Auth Test")
    parser.add_argument(
        "--token", required=True,
        help="Zoho OAuth access token with ZohoCatalyst.projects.users.CREATE scope"
    )
    parser.add_argument(
        "--list-only", action="store_true",
        help="Only list current users, don't create a new one"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  VigilX — Catalyst Authentication Integration Test")
    print("=" * 60)

    if not args.list_only:
        create_catalyst_user(args.token)

    list_catalyst_users(args.token)
    check_providers()

    print("\n" + "=" * 60)
    print("  NEXT STEPS:")
    print("  1. Check your email — Catalyst will send an invite to:")
    print(f"     {TEST_USER['email_id']}")
    print("  2. Accept the invite and set a password.")
    print("  3. Open https://vigilx.onslate.in and log in.")
    print("  4. The backend will auto-create a local user record on first login.")
    print("=" * 60)


if __name__ == "__main__":
    main()
