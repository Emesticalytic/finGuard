import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

from services.llm_service.app import app
import services.llm_service.llm_engine as llm_engine


@pytest.fixture
def mock_anthropic(monkeypatch):
    mock_msg = MagicMock()
    mock_msg.content = [MagicMock(text="This transaction is high risk due to the large amount.")]
    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_msg)
    monkeypatch.setattr(llm_engine, "_client", mock_client)
    return mock_client


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_explain_returns_explanation(client, mock_anthropic):
    resp = await client.post(
        "/explain",
        json={
            "transaction": {"amount": 500.0, "country": "NG", "device_type": "web"},
            "fraud_score": 0.92,
        },
    )
    assert resp.status_code == 200
    assert resp.json()["explanation"] == "This transaction is high risk due to the large amount."
    mock_anthropic.messages.create.assert_awaited_once()


async def test_explain_passes_correct_model(client, mock_anthropic):
    await client.post(
        "/explain",
        json={"transaction": {"amount": 10.0, "country": "US", "device_type": "mobile"}, "fraud_score": 0.1},
    )
    call_kwargs = mock_anthropic.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-sonnet-4-6"
    assert call_kwargs["max_tokens"] == 256


async def test_explain_invalid_payload(client):
    resp = await client.post("/explain", json={"fraud_score": 0.5})
    assert resp.status_code == 422
