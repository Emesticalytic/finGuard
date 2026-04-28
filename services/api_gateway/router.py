import logging

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .config import FRAUD_SERVICE_URL, LLM_SERVICE_URL

logger = logging.getLogger(__name__)
router = APIRouter()


class TransactionRequest(BaseModel):
    transaction_id: str
    amount: float = Field(gt=0)
    is_international: int
    country: str
    device_type: str
    include_explanation: bool = True


class AnalysisResponse(BaseModel):
    transaction_id: str
    fraud_score: float
    risk_bucket: str
    model_version: str
    explanation: str | None


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(req: TransactionRequest):
    transaction = req.model_dump(exclude={"transaction_id", "include_explanation"})

    async with httpx.AsyncClient(timeout=10.0) as client:
        fraud_resp = await client.post(
            f"{FRAUD_SERVICE_URL}/score",
            json={"amount": req.amount, "is_international": req.is_international},
        )
        if fraud_resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Fraud service error")
        fraud_data = fraud_resp.json()
        fraud_score = fraud_data["fraud_score"]
        model_version = fraud_data.get("model_version", "unknown")

    if fraud_score > 0.8:
        risk_bucket = "high"
    elif fraud_score > 0.4:
        risk_bucket = "medium"
    else:
        risk_bucket = "low"

    explanation = None
    if req.include_explanation:
        async with httpx.AsyncClient(timeout=30.0) as client:
            llm_resp = await client.post(
                f"{LLM_SERVICE_URL}/explain",
                json={"transaction": transaction, "fraud_score": fraud_score},
            )
            if llm_resp.status_code == 200:
                explanation = llm_resp.json()["explanation"]
            else:
                logger.warning("LLM service returned %s", llm_resp.status_code)

    return AnalysisResponse(
        transaction_id=req.transaction_id,
        fraud_score=fraud_score,
        risk_bucket=risk_bucket,
        model_version=model_version,
        explanation=explanation,
    )
