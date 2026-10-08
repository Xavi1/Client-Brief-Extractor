from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_returns_healthy():
    """Ensure the /health endpoint returns a 200 status and healthy payload."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_health_check_wrong_method():
    """Ensure non-GET requests to /health are rejected."""
    response = client.post("/health")
    assert response.status_code == 405