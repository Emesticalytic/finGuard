# Model Training — Step by Step

## What Is a Machine Learning Model?

A model is a mathematical function that learns patterns from data.

We showed it 100,000 transactions labelled "fraud" or "not fraud".
It learned: *large amounts + international = more likely fraud.*

After training, it can score brand-new transactions it has never seen before.

---

## The Model We Used: XGBoost

XGBoost is a type of model called a **gradient boosted decision tree**.
It's one of the most popular models for fraud detection in the real world
because it's fast, accurate, and works well on tabular (spreadsheet-style) data.

---

## Step by Step

### Step 1 — Generate Synthetic Data

Real bank transaction data is private. So we generated fake data that
behaves realistically.

```bash
python scripts/generate_synthetic_data.py
```

**Output:** `data/raw/synthetic_transactions.csv`
- 100,000 rows
- Each row = one transaction
- Columns: `amount`, `is_international`, `country`, `device_type`, `is_fraud`

Example rows:
```
amount   is_international   is_fraud
98.76    0                  0        ← safe domestic purchase
4500.00  1                  1        ← fraud: large + international
```

### Step 2 — Train the Model

```bash
python scripts/train_fraud_model.py
```

What this script does:
1. Loads the CSV
2. Splits data: 80% for training, 20% for testing
3. Trains XGBoost on the training set
4. Measures accuracy on the test set
5. Saves the model to `models/fraud_model/`

**Result:** `AUC = 0.943`

AUC (Area Under Curve) measures accuracy:
| AUC | Meaning |
|-----|---------|
| 0.5 | Random guessing |
| 0.7 | Decent |
| 0.9 | Good |
| 0.943 | Excellent ✅ |

### Step 3 — Model is Saved

```
models/fraud_model/
├── model.pkl        ← The actual trained model (binary file)
├── MLmodel          ← MLflow metadata
├── conda.yaml       ← Dependencies
└── requirements.txt
```

The fraud service loads `model.pkl` on startup and keeps it in memory.

---

## How Scoring Works

When a transaction arrives:
```python
X = [[amount, is_international]]   # e.g. [[9999, 1]]
score = model.predict_proba(X)[0, 1]  # probability of fraud
# → 0.9999996
```

Two input features:
- `amount` — higher amounts → higher risk
- `is_international` — 1 means cross-border → higher risk

---

## The Two Features Explained

This model only uses 2 features to keep it simple for learning.
A production fraud model would use 50–200 features including:
- Time of day
- Merchant category
- Distance from home
- Device fingerprint
- Transaction velocity (how many in last hour)

---

## Files Involved

| File | Purpose |
|------|---------|
| [scripts/generate_synthetic_data.py](../scripts/generate_synthetic_data.py) | Creates fake transaction data |
| [scripts/train_fraud_model.py](../scripts/train_fraud_model.py) | Trains and saves the model |
| [scripts/register_model_mlflow.py](../scripts/register_model_mlflow.py) | Registers model in MLflow UI |
| [services/fraud_service/model_loader.py](../services/fraud_service/model_loader.py) | Loads model at runtime |
| [services/fraud_service/app.py](../services/fraud_service/app.py) | Serves predictions via API |
