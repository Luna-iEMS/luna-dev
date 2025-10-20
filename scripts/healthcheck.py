#!/usr/bin/env python3
import requests, sys

API = "http://localhost:8000/health"

print("🔍 Checking API health:", API)
try:
    r = requests.get(API, timeout=5)
    if r.ok:
        print("✅ API healthy:", r.text)
        sys.exit(0)
    else:
        print("❌ API returned", r.status_code)
        sys.exit(1)
except Exception as e:
    print("❌ Healthcheck failed:", e)
    sys.exit(1)
