# Grafana — Step by Step

## What Is Grafana?

Grafana is a dashboarding tool. It takes numbers from your running services
and turns them into live charts and graphs.

Think of it like the dashboard of a car:
- Speedometer = request rate
- Temperature gauge = latency
- Fuel level = error rate

---

## How to Open It

👉 **http://localhost:3000**

**Login:** `admin` / `admin`

---

## How It Works (The Data Flow)

```
Your services (fraud-service, llm-service)
        │
        │  expose /metrics endpoint
        ▼
    Prometheus (9090)
        │
        │  scrapes metrics every 15 seconds
        ▼
      Grafana (3000)
        │
        │  queries Prometheus and draws charts
        ▼
    Dashboard you see
```

---

## What We Did — Step by Step

### Step 1 — Services Expose Metrics

Every service has a `/metrics` endpoint. Try it:
```bash
curl http://localhost:8001/metrics
```

You'll see raw numbers like:
```
fraud_requests_total 5.0
fraud_request_latency_seconds_bucket{le="0.005"} 3.0
...
```

These are **Prometheus-format metrics** — a standard way to expose
numbers from any application.

### Step 2 — Prometheus Scrapes Them

Prometheus visits each `/metrics` URL every 15 seconds and stores the numbers.
Config is in [infra/prometheus/prometheus-config.yaml](../infra/prometheus/prometheus-config.yaml).

### Step 3 — Grafana Reads from Prometheus

Grafana connects to Prometheus as a **datasource** and runs queries to draw charts.

We provisioned the datasource automatically in:
[infra/grafana/provisioning/datasources/prometheus.yaml](../infra/grafana/provisioning/datasources/prometheus.yaml)

### Step 4 — Dashboard Loaded Automatically

The dashboard JSON is at:
[infra/grafana/dashboards/finGuard-dashboard.json](../infra/grafana/dashboards/finGuard-dashboard.json)

Grafana loads it automatically on startup via:
[infra/grafana/provisioning/dashboards/default.yaml](../infra/grafana/provisioning/dashboards/default.yaml)

---

## The Dashboard Panels

| Panel | What it shows |
|-------|--------------|
| Fraud Requests Total | Total number of scoring requests ever made |
| LLM Requests Total | Total number of Claude explanation requests |
| Fraud Request Rate | How many requests per minute right now |
| P99 Latency | The slowest 1% of requests — in milliseconds |
| Inference Latency Over Time | Chart of speed over time (p50, p95, p99) |
| LLM Latency Over Time | Chart of Claude response time over time |

---

## Making the Charts Show Data

Send several transactions quickly and watch the charts update:

```bash
for i in {1..10}; do
  curl -s -X POST http://localhost:8000/v1/analyze \
    -H 'Content-Type: application/json' \
    -d "{\"transaction_id\":\"txn-$i\",\"amount\":$((RANDOM % 10000)),\"is_international\":$((RANDOM % 2)),\"country\":\"US\",\"device_type\":\"web\",\"include_explanation\":false}" \
    > /dev/null
done
echo "Sent 10 transactions"
```

Then refresh Grafana — you'll see the counters go up.

---

## Errors We Fixed

| Error | Cause | Fix |
|-------|-------|-----|
| "Invalid dashboard" | Old `graph` panel type (deprecated in Grafana 10) | Changed to `timeseries` panels |
| No datasource | Missing provisioning files | Created `provisioning/datasources/prometheus.yaml` |
| Wrong password | Container restarted with stale database | Reset with `grafana-cli admin reset-admin-password admin` |
| Dashboard not loading | No provisioning loader | Created `provisioning/dashboards/default.yaml` |
