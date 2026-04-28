# Troubleshooting — Every Error We Hit and How We Fixed It

A log of every problem encountered during setup, what caused it, and how it was resolved.

---

## Error 1: `pyarrow==16.0.0` Dependency Conflict

**Error message:**
```
ERROR: ResolutionImpossible
mlflow 2.13.0 depends on pyarrow<16 and >=4.0.0
```

**Cause:**
`requirements.txt` had `pyarrow==16.0.0` but mlflow 2.13.0 only supports up to version 15.

**Fix:**
Changed `requirements.txt`:
```
pyarrow==15.0.2   ← was 16.0.0
```

---

## Error 2: `attempted relative import with no known parent package`

**Error message:**
```
ImportError: attempted relative import with no known parent package
```

**Cause:**
The Dockerfiles were starting uvicorn like this:
```
WORKDIR /app/services/fraud_service
CMD ["uvicorn", "app:app", ...]
```
When you run a file directly, Python doesn't know about the package structure,
so `from .config import X` fails.

**Fix:**
Changed all Dockerfiles to run from `/app` as the package root:
```
WORKDIR /app
COPY services/ ./services/
CMD ["uvicorn", "services.fraud_service.app:app", ...]
```

Affected files:
- [services/fraud_service/Dockerfile](../services/fraud_service/Dockerfile)
- [services/llm_service/Dockerfile](../services/llm_service/Dockerfile)
- [services/api_gateway/Dockerfile](../services/api_gateway/Dockerfile)

---

## Error 3: `No module named 'pkg_resources'`

**Error message:**
```
ModuleNotFoundError: No module named 'pkg_resources'
```

**Cause:**
Python 3.12-slim doesn't include `setuptools` by default.
`pkg_resources` is part of setuptools and mlflow needs it.

**Fix:**
Rather than fighting this, we changed [services/fraud_service/model_loader.py](../services/fraud_service/model_loader.py)
to load the model with `pickle` directly instead of `mlflow.sklearn.load_model`:

```python
# Before (broken)
import mlflow.sklearn
return mlflow.sklearn.load_model(model_path)

# After (working)
import pickle
with open(Path(model_path) / "model.pkl", "rb") as f:
    return pickle.load(f)
```

---

## Error 4: Port 5432 Already in Use

**Error message:**
```
ports are not available: exposing port TCP 0.0.0.0:5432
```

**Cause:**
A local PostgreSQL installation was already running on port 5432.

**Fix:**
Changed the Docker postgres port mapping in `docker-compose.dev.yml`:
```yaml
ports:
  - "5433:5432"   ← was "5432:5432"
```
The database still listens on 5432 inside Docker, but it's mapped to 5433 on your Mac.

---

## Error 5: Port 5000 Already in Use

**Error message:**
```
ports are not available: exposing port TCP 0.0.0.0:5000
```

**Cause:**
macOS AirPlay Receiver uses port 5000.

**Fix:**
Changed MLflow port in `docker-compose.dev.yml`:
```yaml
ports:
  - "5001:5000"   ← was "5000:5000"
```
MLflow is now at http://localhost:5001.

---

## Error 6: MLflow Version Mismatch

**Error message:**
```
MlflowException: API request to endpoint /api/2.0/mlflow/logged-models failed with error code 404
```

**Cause:**
Local Python has MLflow 3.10.1 but the Docker MLflow image is version 2.13.0.
MLflow 3.x changed its internal API — the client calls endpoints that don't exist in 2.x server.

**Fix:**
MLflow registration via Docker server is not currently working.
The **fraud service does not need MLflow** to run — it loads the model with pickle directly.

To use MLflow UI, run it locally:
```bash
mlflow server --host 127.0.0.1 --port 5002 \
  --backend-store-uri sqlite:///mlruns/mlflow.db
```

---

## Error 7: Grafana "Invalid Dashboard"

**Cause:**
The original dashboard JSON used `"type": "graph"` for chart panels.
The `graph` panel type was removed in Grafana 10.x (replaced by `timeseries`).

**Fix:**
Updated [infra/grafana/dashboards/finGuard-dashboard.json](../infra/grafana/dashboards/finGuard-dashboard.json)
to use `"type": "timeseries"` for all chart panels.

---

## Error 8: Grafana "Invalid username or password"

**Cause:**
Grafana's internal SQLite database was created during an early container start
before the correct password environment variable was applied.
The database remembered the old state even after restart.

**Fix:**
Reset the password via the Grafana CLI:
```bash
docker exec finguard-llm-grafana-1 grafana-cli admin reset-admin-password admin
```

---

## Error 9: Grafana Dashboard Has No Data / No Datasource

**Cause:**
The Grafana container had no provisioning files, so it didn't know:
- Where Prometheus was
- Where to find the dashboard JSON

**Fix:**
Created two provisioning files:

1. [infra/grafana/provisioning/datasources/prometheus.yaml](../infra/grafana/provisioning/datasources/prometheus.yaml)
   — tells Grafana "Prometheus is at http://prometheus:9090"

2. [infra/grafana/provisioning/dashboards/default.yaml](../infra/grafana/provisioning/dashboards/default.yaml)
   — tells Grafana "load dashboard JSONs from /var/lib/grafana/dashboards"

Then mounted the folder in `docker-compose.dev.yml`:
```yaml
volumes:
  - ./infra/grafana/provisioning:/etc/grafana/provisioning
```

---

## Quick Reference: Common Commands

```bash
# Restart a single broken service
docker compose -f docker-compose.dev.yml up --build --force-recreate -d fraud-service

# See why a service crashed
docker compose -f docker-compose.dev.yml logs fraud-service --tail 20

# Reset Grafana password
docker exec finguard-llm-grafana-1 grafana-cli admin reset-admin-password admin

# Check all service health
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
```
