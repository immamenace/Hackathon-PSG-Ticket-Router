from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_mvr_classification_billing():
    response = client.post("/mvr/ticket", json={
        "text": "I need help with my invoice.",
        "user_id": "user123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert data["category"] == "Billing"
    assert data["urgency"] is False

def test_mvr_urgency_regex():
    response = client.post("/mvr/ticket", json={
        "text": "The system is broken, fix it ASAP!",
        "user_id": "user456"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["urgency"] is True

def test_mvr_queue_order():
    # Push a normal ticket
    client.post("/mvr/ticket", json={
        "text": "General question about terms",
        "user_id": "user789"
    })
    # Push an urgent ticket
    client.post("/mvr/ticket", json={
        "text": "Emergency! Server is down ASAP",
        "user_id": "user999"
    })

    # The next ticket popped should be the urgent one
    response = client.get("/mvr/queue/next")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user999"
    assert data["urgency"] is True
