import os

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL_NAME = os.getenv("LLM_MODEL_NAME", "claude-sonnet-4-6")
SERVICE_NAME = "llm_service"
