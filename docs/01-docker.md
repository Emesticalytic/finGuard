# Docker — Step by Step

## What Is Docker?

Think of Docker as a way to package a program with everything it needs to run —
the code, the libraries, the settings — into one sealed box called a **container**.

Without Docker:
> "It works on my machine but not yours" — the classic developer problem.

With Docker:
> Every container runs identically on any machine.

---

## Key Concepts

| Word | Plain meaning |
|------|--------------|
| **Image** | A blueprint (like a recipe) |
| **Container** | A running copy of that blueprint (like a cooked meal) |
| **Docker Compose** | A tool that starts multiple containers at once |
| **Volume** | A folder shared between your computer and a container |
| **Port mapping** | Connecting a container's internal port to your laptop's port |

---

## What We Did — Step by Step

### Step 1 — Installed Docker Desktop
Downloaded and opened Docker Desktop on Mac.
Docker Desktop runs the Docker engine in the background.
You must keep it open whenever you want containers to run.

### Step 2 — Wrote Dockerfiles
Each service has its own `Dockerfile` — instructions for building its image.

Example ([services/fraud_service/Dockerfile](../services/fraud_service/Dockerfile)):
```dockerfile
FROM python:3.12-slim          # Start from a Python image
WORKDIR /app                   # Set working directory
COPY requirements.txt .        # Copy dependency list
RUN pip install ...            # Install all packages
COPY services/ ./services/     # Copy our code
CMD ["uvicorn", ...]           # Command to start the service
```

### Step 3 — Wrote docker-compose.dev.yml
Instead of starting 8 containers manually, one file starts all of them.

```bash
docker compose -f docker-compose.dev.yml up --build -d
```

- `--build` → Build images from Dockerfiles
- `-d` → Run in background (detached)

### Step 4 — Fixed Errors Along the Way

| Error | Cause | Fix |
|-------|-------|-----|
| `pyarrow==16.0.0` conflict | mlflow needs `<16` | Changed to `pyarrow==15.0.2` |
| `attempted relative import` | Wrong uvicorn start path | Changed to `uvicorn services.fraud_service.app:app` |
| `No module named pkg_resources` | Python 3.12 missing setuptools | Loaded model with `pickle` instead of mlflow |
| Port 5432 in use | Local PostgreSQL already running | Mapped Docker postgres to port 5433 |
| Port 5000 in use | macOS AirPlay Receiver | Mapped MLflow to port 5001 |

---

## Daily Commands

```bash
# Start everything
docker compose -f docker-compose.dev.yml up -d

# Stop everything
docker compose -f docker-compose.dev.yml down

# See what's running
docker compose -f docker-compose.dev.yml ps

# See live logs
docker compose -f docker-compose.dev.yml logs -f

# See logs for one service
docker compose -f docker-compose.dev.yml logs fraud-service

# Rebuild one service after code change
docker compose -f docker-compose.dev.yml up --build -d fraud-service
```

---

## What's Running Right Now

```
CONTAINER                    PORT     STATUS
finguard-llm-api-gateway     8000     ✅ Up
finguard-llm-fraud-service   8001     ✅ Up
finguard-llm-llm-service     8002     ✅ Up
finguard-llm-postgres         5433     ✅ Healthy
finguard-llm-redis            6379     ✅ Healthy
finguard-llm-mlflow           5001     ✅ Up
finguard-llm-prometheus       9090     ✅ Up
finguard-llm-grafana          3000     ✅ Up
```
