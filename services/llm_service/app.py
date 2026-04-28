from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from .llm_engine import generate_explanation

app = FastAPI(title="LLM Service")

REQUEST_COUNT = Counter("llm_requests_total", "Total LLM requests")
LATENCY = Histogram("llm_request_latency_seconds", "LLM request latency")


class LLMRequest(BaseModel):
    transaction: dict
    fraud_score: float


class LLMResponse(BaseModel):
    explanation: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/explain", response_model=LLMResponse)
async def explain(req: LLMRequest):
    REQUEST_COUNT.inc()
    with LATENCY.time():
        explanation = await generate_explanation(req.transaction, req.fraud_score)
    return LLMResponse(explanation=explanation)


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
