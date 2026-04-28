# finGuard-LLM

Real-time financial fraud detection platform combining a classical ML fraud scoring service with an LLM-powered explanation engine.

## Architecture

```
Client → API Gateway → Fraud Service (XGBoost/LightGBM)
                     → LLM Service   (Claude / GPT-4 via Anthropic SDK)
                     → Feature Store (Feast)
                     → PostgreSQL + Redis
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| api-gateway | 8000 | Request routing, auth, rate limiting |
| fraud-service | 8001 | ML inference, feature retrieval |
| llm-service | 8002 | LLM explanation generation |

## Quick Start (Docker)

```bash
cp .env.example .env          # fill in ANTHROPIC_API_KEY, DB_URL, etc.
docker compose -f docker-compose.dev.yml up --build
```

## Quick Start (Kubernetes)

```bash
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/
```

## Model Training

```bash
python scripts/generate_synthetic_data.py
python scripts/train_fraud_model.py
python scripts/register_model_mlflow.py
```

## Monitoring

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000  
- MLflow: http://localhost:5000

## Stack

- **Inference**: FastAPI + Uvicorn
- **ML**: XGBoost, scikit-learn, MLflow
- **LLM**: Anthropic Claude (claude-sonnet-4-6)
- **Feature Store**: Feast + Redis
- **Storage**: PostgreSQL, Redis
- **Observability**: OpenTelemetry, Prometheus, Grafana
- **Orchestration**: Kubernetes + HPA
