import anthropic

from .config import ANTHROPIC_API_KEY, MODEL_NAME

_client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = (
    "You are a fraud analyst assistant. Given a transaction and a fraud score, "
    "explain in clear, concise language why the transaction might be risky or safe. "
    "Always reference the amount, country, and device type."
)


async def generate_explanation(transaction: dict, fraud_score: float) -> str:
    user_prompt = (
        f"Transaction: {transaction}. "
        f"Fraud score: {fraud_score:.3f}. "
        "Explain the risk in under 120 words."
    )

    message = await _client.messages.create(
        model=MODEL_NAME,
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text.strip()