import os

FRAUD_SERVICE_URL = os.getenv("FRAUD_SERVICE_URL", "http://fraud-service:8001")
LLM_SERVICE_URL = os.getenv("LLM_SERVICE_URL", "http://llm-service:8002")
SERVICE_NAME = "api_gateway"
