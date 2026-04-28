"""
Registers the trained model in MLflow Model Registry and promotes it to Production.
Run after train_fraud_model.py has saved models/fraud_model.
"""

import os
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd

MODEL_PATH = Path("models/fraud_model")
FEATURES_PATH = Path("data/processed/features.parquet")
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
REGISTERED_NAME = "fraud_detector"

mlflow.set_tracking_uri(MLFLOW_URI)
mlflow.set_experiment("fraud_detection")


def register():
    import pickle
    with open(MODEL_PATH / "model.pkl", "rb") as f:
        model = pickle.load(f)

    df = pd.read_parquet(FEATURES_PATH)
    sample = df[["amount", "is_international"]].head(5)

    with mlflow.start_run(run_name="xgb-registration") as run:
        mlflow.log_params(
            {
                "n_estimators": model.n_estimators,
                "max_depth": model.max_depth,
                "learning_rate": model.learning_rate,
            }
        )
        mlflow.sklearn.log_model(model, artifact_path="model", input_example=sample)
        run_id = run.info.run_id

    mv = mlflow.register_model(f"runs:/{run_id}/model", REGISTERED_NAME)

    client = mlflow.tracking.MlflowClient()
    client.transition_model_version_stage(
        name=REGISTERED_NAME,
        version=mv.version,
        stage="Production",
        archive_existing_versions=True,
    )
    print(f"Registered run {run_id} → {REGISTERED_NAME} v{mv.version} @ Production")


if __name__ == "__main__":
    register()
