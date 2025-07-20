from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)

# PUBLIC_INTERFACE
def test_health_check():
    """Test the root health check endpoint returns expected structure."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Healthy"}
