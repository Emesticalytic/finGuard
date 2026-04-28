# finGuard — What Is This Project?

## The Problem It Solves

Every time someone swipes a credit card, a bank must decide in milliseconds:
**"Is this real, or is it fraud?"**

finGuard does exactly that. It combines two types of AI:
1. A **machine learning model** (XGBoost) that scores every transaction 0–1
2. A **language model** (Claude) that explains in plain English why it's suspicious

---

## How a Transaction Flows Through the System

```
You (or a bank app)
        │
        ▼
┌─────────────────┐
│   API Gateway   │  ← Receives the transaction request
│   port 8000     │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐  ┌─────────┐
│ Fraud  │  │   LLM   │
│Service │  │ Service │
│  :8001 │  │  :8002  │
└───┬────┘  └────┬────┘
    │             │
    │ score 0–1   │ explanation text
    └──────┬──────┘
           ▼
    Response to you:
    {
      "fraud_score": 0.99,
      "risk_bucket": "high",
      "explanation": "Large international transfer..."
    }
```

---

## The Three Risk Buckets

| Score | Bucket | Meaning |
|-------|--------|---------|
| 0.00 – 0.40 | `low` | Almost certainly safe |
| 0.40 – 0.80 | `medium` | Worth reviewing |
| 0.80 – 1.00 | `high` | Likely fraud — block it |

---

## All the Tools Used and Why

| Tool | Port | Purpose |
|------|------|---------|
| API Gateway | 8000 | Front door — routes requests |
| Fraud Service | 8001 | ML scoring with XGBoost |
| LLM Service | 8002 | Claude AI explanations |
| PostgreSQL | 5433 | Persistent database |
| Redis | 6379 | Fast cache / feature store |
| MLflow | 5001 | Tracks model training experiments |
| Prometheus | 9090 | Collects live metrics from services |
| Grafana | 3000 | Visualises metrics as charts |

---

## Docs in This Folder

| File | What it covers |
|------|----------------|
| [01-docker.md](01-docker.md) | What Docker is and how we used it |
| [02-model-training.md](02-model-training.md) | How the fraud AI model was built |
| [03-api.md](03-api.md) | How to call the API and what you get back |
| [04-grafana.md](04-grafana.md) | How to read the Grafana dashboard |
| [05-prometheus.md](05-prometheus.md) | How Prometheus collects metrics |
| [06-mlflow.md](06-mlflow.md) | How MLflow tracks experiments |
| [07-kubernetes.md](07-kubernetes.md) | What Kubernetes is and when you need it |
| [08-troubleshooting.md](08-troubleshooting.md) | Fixes for every error we hit |
