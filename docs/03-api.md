# The API — Step by Step

## What Is an API?

An API (Application Programming Interface) is a way for programs to talk to each other
over the internet using HTTP — the same protocol your browser uses.

You send a **request** → you get back a **response**.

---

## Your API Has One Main Endpoint

```
POST http://localhost:8000/v1/analyze
```

`POST` means you're sending data (the transaction).
`/v1/analyze` is the path — like a URL on a website.

---

## Interactive Docs (Swagger UI)

Open this in your browser:
👉 **http://localhost:8000/docs**

Swagger is an auto-generated webpage that lets you test the API
by clicking buttons — no terminal needed.

---

## How to Call the API

### From the Terminal (curl)

```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H 'Content-Type: application/json' \
  -d '{
    "transaction_id": "txn-001",
    "amount": 1,
    "is_international": 0,
    "country": "US",
    "device_type": "web",
    "include_explanation": true
  }'
```

### The Fields You Send

| Field | Type | Example | Meaning |
|-------|------|---------|---------|
| `transaction_id` | text | `"txn-001"` | Any unique ID you choose |
| `amount` | number | `4500.00` | Transaction amount in dollars |
| `is_international` | 0 or 1 | `1` | 0 = domestic, 1 = cross-border |
| `country` | text | `"NG"` | Country code |
| `device_type` | text | `"mobile"` | web, mobile, atm, etc. |
| `include_explanation` | true/false | `true` | Whether to ask Claude for explanation |

---

## What You Get Back

```json
{
  "transaction_id": "txn-001",
  "fraud_score": 0.012,
  "risk_bucket": "low",
  "model_version": "v1",
  "explanation": null
}
```

| Field | Meaning |
|-------|---------|
| `fraud_score` | 0.0 to 1.0 — probability of fraud |
| `risk_bucket` | `low` / `medium` / `high` |
| `model_version` | Which model version scored it |
| `explanation` | Claude's text explanation (null = needs Anthropic credits) |

---

## Try These Examples and Compare

### Low Risk — Small domestic purchase
```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H 'Content-Type: application/json' \
  -d '{"transaction_id":"safe-1","amount":12.50,"is_international":0,"country":"US","device_type":"web","include_explanation":false}'
```
Expected: `fraud_score` near **0.01**, `risk_bucket: "low"`

---

### High Risk — Large international transfer
```bash
curl -X POST http://localhost:8000/v1/analyze \
  -H 'Content-Type: application/json' \
  -d '{"transaction_id":"risky-1","amount":9999.99,"is_international":1,"country":"NG","device_type":"mobile","include_explanation":false}'
```
Expected: `fraud_score` near **0.999**, `risk_bucket: "high"`

---

## How the Three Services Work Together

```
Your curl request
      │
      ▼
API Gateway (8000)
  router.py receives it
      │
      ├──► Fraud Service (8001)  POST /score
      │         Returns: { "fraud_score": 0.99 }
      │
      └──► LLM Service (8002)   POST /explain
                Returns: { "explanation": "..." }
      │
      ▼
API Gateway assembles final response
      │
      ▼
Response back to you
```

---

## Health Checks

Each service has a `/health` endpoint to confirm it's alive:

```bash
curl http://localhost:8000/health   # API Gateway
curl http://localhost:8001/health   # Fraud Service
curl http://localhost:8002/health   # LLM Service
```

All should return: `{"status": "ok"}`

---

## Files Involved

| File | Purpose |
|------|---------|
| [services/api_gateway/router.py](../services/api_gateway/router.py) | Handles `/v1/analyze`, calls other services |
| [services/fraud_service/app.py](../services/fraud_service/app.py) | Handles `/score`, runs XGBoost |
| [services/llm_service/app.py](../services/llm_service/app.py) | Handles `/explain`, calls Claude |
| [services/llm_service/llm_engine.py](../services/llm_service/llm_engine.py) | Anthropic SDK integration |
