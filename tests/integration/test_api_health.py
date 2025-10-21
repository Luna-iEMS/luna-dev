import httpx

def test_health_endpoint():
    """Simple health check."""
    r = httpx.get("http://localhost:8000/health", timeout=10)
    assert r.status_code == 200
    assert "status" in r.json()
