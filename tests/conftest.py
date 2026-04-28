from unittest.mock import MagicMock, patch
import numpy as np


def pytest_configure(config):
    """Patch model loader before any service modules are imported."""
    mock_model = MagicMock()
    mock_model.predict_proba.return_value = np.array([[0.08, 0.92]])
    patch("services.fraud_service.model_loader.load_model", return_value=mock_model).start()
