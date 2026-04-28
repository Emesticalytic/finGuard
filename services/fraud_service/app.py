from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from .config import MODEL_PATH
from .model_loader import load_model

app = FastAPI(title="Fraud Service")

model = load_model(MODEL_PATH)

REQUEST_COUNT = Counter("fraud_requests_total", "Total fraud requests")
LATENCY = Histogram("fraud_request_latency_seconds", "Fraud request latency")

class Transaction(BaseModel):
    amount: float
    is_international: int

class FraudScore(BaseModel):
    fraud_score: float
    model_version: str = "v1"

@app.post("/score", response_model=FraudScore)
def score(txn: Transaction):
    REQUEST_COUNT.inc()
    with LATENCY.time():
        X = np.array([[txn.amount, txn.is_international]])
        prob = float(model.predict_proba(X)[0, 1])
        return FraudScore(fraud_score=prob)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
