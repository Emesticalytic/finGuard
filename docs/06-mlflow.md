# MLflow — Step by Step

## What Is MLflow?

MLflow is an experiment tracker for machine learning.

Every time you train a model you're running an **experiment**:
- You try different settings (e.g. 100 trees vs 200 trees)
- You compare results (which AUC was better?)
- You save the winning model

MLflow records all of this automatically so you never lose track
of what you tried and what worked.

---

## How to Open It

👉 **http://localhost:5001**

---

## What Gets Tracked

When you ran `python scripts/train_fraud_model.py`, MLflow recorded:

| What | Example |
|------|---------|
| Parameters | `n_estimators=200`, `max_depth=4` |
| Metrics | `auc=0.943` |
| The model itself | Saved as an artifact |
| Run ID | Unique ID for this training run |

---

## Step by Step — What Happened

### Step 1 — Training Was Run Locally

```bash
python scripts/generate_synthetic_data.py  # Generate 100,000 transactions
python scripts/train_fraud_model.py        # Train XGBoost, AUC = 0.943
```

This logged a run to a local SQLite database (`mlruns/` folder).

### Step 2 — MLflow Server Started in Docker

The Docker MLflow server runs at http://localhost:5001 but uses
its **own separate** database inside the container.

### Step 3 — Version Conflict (What Went Wrong)

| Location | MLflow Version |
|----------|---------------|
| Your local Python (Anaconda) | 3.10.1 |
| Docker MLflow image | 2.13.0 |

MLflow 3.x changed its API — the local client tries to call endpoints
that don't exist in the 2.13.0 server. This caused the registration to fail.

### Step 4 — Workaround (Run MLflow Locally)

To see your model in MLflow UI, run the server locally instead of Docker:

```bash
# Terminal 1 — Start local MLflow server
mlflow server --host 127.0.0.1 --port 5002 \
  --backend-store-uri sqlite:///mlruns/mlflow.db

# Terminal 2 — Register the model
MLFLOW_TRACKING_URI=http://localhost:5002 python scripts/train_fraud_model.py
MLFLOW_TRACKING_URI=http://localhost:5002 python scripts/register_model_mlflow.py
```

Then open http://localhost:5002 — you'll see the experiment and model.

---

## Important: MLflow Is Not Needed at Runtime

The fraud service does **not** need MLflow to score transactions.
It loads the model directly from `models/fraud_model/model.pkl`.

MLflow is only for:
- Viewing experiment history
- Comparing model versions
- A team knowing "which model is in production"

The fraud detection works perfectly without it.

---

## Key Terms

| Term | Meaning |
|------|---------|
| **Experiment** | A named group of training runs (e.g. "fraud_detection") |
| **Run** | One training execution with its own parameters + metrics |
| **Artifact** | A file saved by a run (e.g. the model file) |
| **Model Registry** | A catalogue of registered models with version history |
| **Stage** | Where a model version is: Staging → Production → Archived |
