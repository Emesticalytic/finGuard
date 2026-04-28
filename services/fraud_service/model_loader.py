import pickle
from pathlib import Path

from sklearn.base import BaseEstimator

def load_model(model_path: str) -> BaseEstimator:
    pkl_path = Path(model_path) / "model.pkl"
    if pkl_path.exists():
        with open(pkl_path, "rb") as f:
            return pickle.load(f)
    raise FileNotFoundError(f"Model not found at {model_path}")
