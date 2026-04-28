# Kubernetes — What It Is and When You Need It

## What Is Kubernetes?

Kubernetes (K8s) is a system for running containers in the **cloud at scale**.

Docker Compose runs containers on **your laptop**.
Kubernetes runs containers across **many servers in the cloud**.

---

## The Simple Analogy

| | Docker Compose | Kubernetes |
|--|---------------|------------|
| Where | Your laptop | Cloud (AWS, GCP, Azure) |
| Scale | 1 machine | 10s or 100s of machines |
| Traffic | Low (dev/test) | High (production) |
| Self-healing | No | Yes — restarts crashed containers |
| Auto-scaling | No | Yes — adds more copies under load |

---

## Why We Have K8s Files But Aren't Using Them

The files in [infra/k8s/](../infra/k8s/) are the production deployment configs.
They exist because a real bank would deploy finGuard to Kubernetes.

For **learning purposes**, Docker Compose on your laptop is enough.
You don't need Kubernetes unless you're deploying to a real cloud server.

---

## What's in the K8s Folder

```
infra/k8s/
├── namespace.yaml              ← Creates an isolated "finguard" space
├── api-gateway-deployment.yaml ← Runs 2 copies of the API gateway
├── fraud-service-deployment.yaml
├── llm-service-deployment.yaml
├── postgres.yaml               ← Database
├── redis.yaml                  ← Cache
├── hpa.yaml                    ← Auto-scaling rules
└── ingress.yaml                ← Public URL routing
```

---

## Key Kubernetes Concepts

| Word | Plain meaning |
|------|--------------|
| **Pod** | One running container (like a Docker container) |
| **Deployment** | Manages pods — keeps N copies alive |
| **Service** | A stable address to reach a set of pods |
| **Ingress** | The public-facing URL that routes to services |
| **HPA** | Horizontal Pod Autoscaler — adds pods under load |
| **Namespace** | An isolated section of the cluster (like a folder) |

---

## When You Would Use Kubernetes

1. You want finGuard available 24/7 on the internet
2. You expect high traffic (thousands of requests per second)
3. You want automatic recovery if a container crashes
4. You want to scale up during peak hours and scale down at night

---

## How to Deploy to Kubernetes (When Ready)

You need a running cluster first. Options:
- **Local test**: Enable Kubernetes in Docker Desktop → Settings → Kubernetes
- **Cloud**: Create a cluster on AWS EKS, GCP GKE, or Azure AKS

Then:
```bash
# Create the namespace
kubectl apply -f infra/k8s/namespace.yaml

# Deploy everything
kubectl apply -f infra/k8s/

# Check pods are running
kubectl get pods -n finguard

# Get the public URL
kubectl get ingress -n finguard
```

---

## Summary

- **Right now**: Docker Compose ✅ — perfect for learning
- **Going to production**: Kubernetes — for real cloud deployment
- **The K8s files are already written** — they're waiting until you need them
