from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check_root():
    """Verify GET /health returns expected status and service payload."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "homemind",
    }


def test_health_check_api_prefix():
    """Verify GET /api/health also returns expected payload."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "homemind",
    }
