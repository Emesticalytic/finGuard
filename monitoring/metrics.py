from prometheus_client import Counter, Gauge, Histogram

INFERENCE_LATENCY = Histogram(
    "finguard_inference_duration_seconds",
    "ML model inference latency in seconds",
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)

LLM_LATENCY = Histogram(
    "finguard_llm_duration_seconds",
    "LLM explanation generation latency in seconds",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0],
)

TRANSACTIONS_TOTAL = Counter(
    "finguard_transactions_total",
    "Total number of transactions scored",
)

FRAUD_DETECTED_TOTAL = Counter(
    "finguard_fraud_detected_total",
    "Total transactions flagged as fraudulent",
)

FRAUD_SCORE = Histogram(
    "finguard_fraud_score",
    "Distribution of fraud scores",
    buckets=[0.1 * i for i in range(11)],
)

MODEL_VERSION = Gauge(
    "finguard_model_version",
    "Current model version loaded",
)
