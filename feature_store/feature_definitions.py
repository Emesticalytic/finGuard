from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Int64, Float32, String

transactions_source = FileSource(
    path="data/processed/features.parquet",
    timestamp_field="event_timestamp",
)

customer = Entity(name="customer_id", join_keys=["customer_id"])

fraud_features_view = FeatureView(
    name="fraud_features",
    entities=[customer],
    ttl=timedelta(days=1),
    schema=[
        Field(name="avg_amount_7d", dtype=Float32),
        Field(name="txn_count_7d", dtype=Int64),
        Field(name="intl_txn_ratio_30d", dtype=Float32),
        Field(name="country", dtype=String),
    ],
    online=True,
    source=transactions_source,
)
