from fastapi.testclient import TestClient

from app.main import app


def test_healthz_ok():
    client = TestClient(app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_expoe_travas_operacionais():
    client = TestClient(app)

    response = client.get("/readyz")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["safety_ok"] is True
    assert body["human_review_required"] is True
    assert body["official_sei_actions_allowed"] is False
