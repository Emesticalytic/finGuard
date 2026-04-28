import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from xgboost import XGBClassifier
import mlflow
import mlflow.sklearn

mlflow.set_experiment("fraud_detection")

def main():
    df = pd.read_csv("data/raw/synthetic_transactions.csv")

    features = ["amount", "is_international"]
    X = df[features]
    y = df["is_fraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    with mlflow.start_run():
        model = XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
        )
        model.fit(X_train, y_train)
        y_pred = model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, y_pred)

        mlflow.log_metric("auc", auc)
        mlflow.log_params(model.get_params())
        mlflow.sklearn.log_model(model, "model")

        run_id = mlflow.active_run().info.run_id
        print(f"Model trained. AUC={auc:.3f}, run_id={run_id}")

        Path("models").mkdir(exist_ok=True)
        mlflow.sklearn.save_model(model, "models/fraud_model")

if __name__ == "__main__":
    main()
