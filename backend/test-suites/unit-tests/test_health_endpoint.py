from fastapi.testclient import TestClient
from scout.main import app
client = TestClient(app)
def test_health_endpoint_returns_healthy_status() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "thungatha-scout-api"}
