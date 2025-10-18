import requests

print("🔍 Running Luna-IEMS Smoke Test...")

resp = requests.get("http://localhost:8000/api/v1/system/info", timeout=5)
print(f"✅ API Response: {resp.status_code} - {resp.json()['status']}")
