import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from services.api_gateway.app import app

ANALYZE_URL = "/v1/analyze"

BASE_PAYLOAD = {
    "transaction_id": "txn-001",
    "amount": 500.0,
    "is_international": 1,
    "country": "NG",
    "device_type": "web",
}


def _make_downstream_mock(fraud_score: float, model_version: str = "v1", explanation: str = "Risky."):
    """Return a patched httpx.AsyncClient that serves canned fraud + LLM responses."""
    responses = [
        MagicMock(status_code=200, json=MagicMock(return_value={"fraud_score": fraud_score, "model_version": model_version})),
        MagicMock(status_code=200, json=MagicMock(return_value={"explanation": explanation})),
    ]
    call_idx = {"i": 0}

    async def mock_post(*args, **kwargs):
        resp = responses[call_idx["i"]]
        call_idx["i"] += 1
        return resp

    mock_client = AsyncMock()
    mock_client.post = mock_post
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200


async def test_analyze_high_risk(client):
    mock = _make_downstream_mock(fraud_score=0.92)
    with patch("services.api_gateway.router.httpx.AsyncClient", return_value=mock):
        resp = await client.post(ANALYZE_URL, json=BASE_PAYLOAD)

    assert resp.status_code == 200
    data = resp.json()
    assert data["fraud_score"] == 0.92
    assert data["risk_bucket"] == "high"
    assert data["model_version"] == "v1"
    assert data["explanation"] == "Risky."


async def test_analyze_medium_risk(client):
    mock = _make_downstream_mock(fraud_score=0.55)
    with patch("services.api_gateway.router.httpx.AsyncClient", return_value=mock):
        resp = await client.post(ANALYZE_URL, json={**BASE_PAYLOAD, "amount": 100.0})

    assert resp.json()["risk_bucket"] == "medium"


async def test_analyze_low_risk(client):
    mock = _make_downstream_mock(fraud_score=0.1)
    with patch("services.api_gateway.router.httpx.AsyncClient", return_value=mock):
        resp = await client.post(ANALYZE_URL, json={**BASE_PAYLOAD, "amount": 5.0})

    assert resp.json()["risk_bucket"] == "low"


async def test_analyze_no_explanation(client):
    responses = [
        MagicMock(status_code=200, json=MagicMock(return_value={"fraud_score": 0.3, "model_version": "v1"})),
    ]
    call_idx = {"i": 0}

    async def mock_post(*args, **kwargs):
        resp = responses[call_idx["i"]]
        call_idx["i"] += 1
        return resp

    mock_client = AsyncMock()
    mock_client.post = mock_post
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("services.api_gateway.router.httpx.AsyncClient", return_value=mock_client):
        resp = await client.post(ANALYZE_URL, json={**BASE_PAYLOAD, "include_explanation": False})

    data = resp.json()
    assert data["explanation"] is None


async def test_analyze_fraud_service_down(client):
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=MagicMock(status_code=503))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("services.api_gateway.router.httpx.AsyncClient", return_value=mock_client):
        resp = await client.post(ANALYZE_URL, json=BASE_PAYLOAD)

    assert resp.status_code == 502


async def test_analyze_invalid_amount(client):
    resp = await client.post(ANALYZE_URL, json={**BASE_PAYLOAD, "amount": -10.0})
    assert resp.status_code == 422


async def test_analyze_missing_field(client):
    resp = await client.post(ANALYZE_URL, json={"transaction_id": "txn-001", "amount": 100.0})
    assert resp.status_code == 422
