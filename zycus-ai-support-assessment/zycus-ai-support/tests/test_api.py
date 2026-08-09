from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_triage_api():
    response = client.post("/triage", json={"subject":"Something is wrong", "body":"It is not working."})
    assert response.status_code == 200
    assert "urgency" in response.json()


def test_account_health_api():
    response = client.post("/account-health", json={"account_id":"ACC-3336"})
    assert response.status_code == 200
    assert response.json()["account_id"] == "ACC-3336"
