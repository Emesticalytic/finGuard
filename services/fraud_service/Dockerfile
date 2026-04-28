FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir setuptools && pip install --no-cache-dir -r requirements.txt

COPY models/fraud_model ./models/fraud_model
COPY services/ ./services/

ENV MODEL_PATH=/app/models/fraud_model

CMD ["uvicorn", "services.fraud_service.app:app", "--host", "0.0.0.0", "--port", "8001"]
