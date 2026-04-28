import numpy as np
import pandas as pd
from pathlib import Path

N = 100_000
np.random.seed(42)

def generate():
    customer_ids = np.random.randint(1, 10_000, size=N)
    merchant_ids = np.random.randint(1, 2_000, size=N)
    amounts = np.round(np.random.exponential(50, size=N), 2)
    countries = np.random.choice(["UK", "US", "NG", "DE", "FR"], size=N)
    device_types = np.random.choice(["mobile", "web", "pos"], size=N)
    is_international = np.random.binomial(1, 0.2, size=N)
    label = (
        (amounts > 200).astype(int)
        | (is_international & (device_types == "web")).astype(int)
    )

    df = pd.DataFrame(
        {
            "transaction_id": np.arange(N),
            "customer_id": customer_ids,
            "merchant_id": merchant_ids,
            "amount": amounts,
            "country": countries,
            "device_type": device_types,
            "is_international": is_international,
            "is_fraud": label,
        }
    )
    out_path = Path("data/raw/synthetic_transactions.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    generate()
