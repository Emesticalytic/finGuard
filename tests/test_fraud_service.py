import pytest
from httpx import AsyncClient, ASGITransport

from services.fraud_service.app import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_score_returns_fraud_score(client):
    resp = await client.post("/score", json={"amount": 500.0, "is_international": 1})
    assert resp.status_code == 200
    data = resp.json()
    assert abs(data["fraud_score"] - 0.92) < 1e-6
    assert data["model_version"] == "v1"


async def test_score_low_amount(client):
    resp = await client.post("/score", json={"amount": 10.0, "is_international": 0})
    assert resp.status_code == 200
    assert "fraud_score" in resp.json()


async def test_score_invalid_payload(client):
    resp = await client.post("/score", json={"amount": "not-a-number", "is_international": 0})
    assert resp.status_code == 422


async def test_metrics_endpoint(client):
    resp = await client.get("/metrics")
    assert resp.status_code == 200
    assert "fraud_requests_total" in resp.text
