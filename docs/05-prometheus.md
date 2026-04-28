# Prometheus — Step by Step

## What Is Prometheus?

Prometheus is a **metrics collector**. It regularly visits your services,
reads numbers from them, and stores those numbers over time.

It does NOT show charts. It just stores the raw data.
Grafana then reads from Prometheus to draw the charts.

---

## How to Open It

👉 **http://localhost:9090**

You can type queries here directly and see raw results.

---

## How It Works

Every 15 seconds, Prometheus visits each service's `/metrics` URL
and saves the numbers it finds.

```
Every 15 seconds:
  GET http://fraud-service:8001/metrics
  GET http://llm-service:8002/metrics
  GET http://api-gateway:8000/metrics
```

---

## The Config File

[infra/prometheus/prometheus-config.yaml](../infra/prometheus/prometheus-config.yaml)

This tells Prometheus which services to scrape.

---

## Metrics Your Services Expose

### Fraud Service
| Metric | Meaning |
|--------|---------|
| `fraud_requests_total` | Total requests ever |
| `fraud_request_latency_seconds` | How long each request took |

### LLM Service
| Metric | Meaning |
|--------|---------|
| `llm_requests_total` | Total Claude requests ever |
| `llm_request_latency_seconds` | How long Claude took to respond |

---

## Trying a Query

Open http://localhost:9090 and type in the search box:

```
fraud_requests_total
```

You'll see the current count of fraud scoring requests.

Try this one to see request rate per minute:
```
rate(fraud_requests_total[1m]) * 60
```

---

## Why Bother With Prometheus?

In production, you want to know:
- Is my service getting slower over time?
- How many requests am I handling?
- When did something break?

Prometheus answers all of these by storing history,
so you can look back and say "the latency spiked at 3pm on Tuesday."
