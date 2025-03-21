from fastapi.testclient import TestClient
from api.main import app  # ✅ FIXED IMPORT
import os

client = TestClient(app)

def test_health_endpoint():
    """
    Test the health check endpoint
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

print("Hello World")