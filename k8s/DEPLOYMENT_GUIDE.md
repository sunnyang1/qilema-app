# Qilema Kubernetes Deployment Guide

Your Kubernetes manifests have been generated in the `k8s/` directory. This guide explains each component and provides deployment instructions.

## Architecture Overview

The manifests deploy a 4-service architecture across Kubernetes:

- **PostgreSQL** (1 replica) - persistent relational database
- **Redis** (1 replica) - in-memory cache
- **Backend** (2 replicas, HPA-managed 2-5) - FastAPI application
- **Nginx** (2 replicas) - reverse proxy and ingress

All services run in the `qilema` namespace with health checks, resource limits, and security contexts.

## File Inventory

### Infrastructure

| File | Purpose |
|------|---------|
| `namespace.yaml` | Creates `qilema` namespace for all resources |

### PostgreSQL

| File | Purpose |
|------|---------|
| `postgres-configmap.yaml` | Database name and user configuration |
| `postgres-secret.yaml` | Database password (change before production) |
| `postgres-pvc.yaml` | 10Gi persistent volume for data |
| `postgres-deployment.yaml` | Database pod with liveness/readiness probes |
| `postgres-service.yaml` | ClusterIP service for backend/internal access |

### Redis

| File | Purpose |
|------|---------|
| `redis-configmap.yaml` | Memory limits and eviction policy |
| `redis-pvc.yaml` | 5Gi persistent volume for data |
| `redis-deployment.yaml` | Cache pod with health checks |
| `redis-service.yaml` | ClusterIP service for backend access |

### Backend

| File | Purpose |
|------|---------|
| `backend-configmap.yaml` | Environment config (DATABASE_URL, REDIS_URL, LOG_LEVEL, etc.) |
| `backend-secret.yaml` | SECRET_KEY and ENCRYPTION_KEY (change before production) |
| `backend-deployment.yaml` | 2 replicas with rolling updates and pod anti-affinity |
| `backend-service.yaml` | ClusterIP service for nginx access |

### Nginx

| File | Purpose |
|------|---------|
| `nginx-configmap.yaml` | Nginx config and default upstream to backend:8000 |
| `nginx-deployment.yaml` | 2 replicas with rolling updates and pod anti-affinity |
| `nginx-service.yaml` | LoadBalancer service (change to NodePort if needed) |

### Ingress & Autoscaling

| File | Purpose |
|------|---------|
| `ingress.yaml` | HTTPS ingress with Let's Encrypt (requires cert-manager) |
| `backend-hpa.yaml` | HPA to scale backend 2-5 replicas on CPU/memory load |

## Pre-Deployment Checklist

### 1. Kubernetes Cluster Setup

```bash
# Verify cluster is running
kubectl cluster-info

# Check nodes
kubectl get nodes

# Recommended: EKS, GKE, AKS, or local cluster (kind, minikube)
```

### 2. Build and Push Backend Image

Your backend image must exist in a container registry before deployment:

```bash
# Build the image
docker build -t your-registry/qilema-backend:latest ./backend

# Push to registry
docker push your-registry/qilema-backend:latest
```

Update the image reference in `k8s/backend-deployment.yaml`:
```yaml
image: your-registry/qilema-backend:latest  # Change this
```

### 3. Update Secrets

Open `k8s/backend-secret.yaml` and `k8s/postgres-secret.yaml`, replace placeholder values:

```yaml
# postgres-secret.yaml
stringData:
  POSTGRES_PASSWORD: "your-strong-password-here"

# backend-secret.yaml
stringData:
  SECRET_KEY: "your-app-secret-key"
  ENCRYPTION_KEY: "your-encryption-key"
```

### 4. Update ConfigMaps (Optional)

Edit `k8s/backend-configmap.yaml` if needed:
- Change `POSTGRES_PASSWORD` to match the secret
- Adjust `LOG_LEVEL` (DEBUG, INFO, WARNING, ERROR)
- Update `DATABASE_URL` if not using default `qilema` namespace

### 5. Ingress & TLS (Optional)

For HTTPS, you need:

**Option A: cert-manager + Let's Encrypt**
```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

Edit `k8s/ingress.yaml`:
```yaml
- host: your-domain.com  # Change this
```

**Option B: Skip HTTPS for now**
Delete `k8s/ingress.yaml` and expose via `kubectl port-forward`:
```bash
kubectl port-forward -n qilema svc/nginx 80:80
# API accessible at http://localhost
```

## Deployment Steps

### Step 1: Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

### Step 2: Create ConfigMaps and Secrets

```bash
# Create secrets (DO NOT commit to git!)
kubectl apply -f k8s/postgres-secret.yaml
kubectl apply -f k8s/backend-secret.yaml

# Create configs
kubectl apply -f k8s/postgres-configmap.yaml
kubectl apply -f k8s/redis-configmap.yaml
kubectl apply -f k8s/backend-configmap.yaml
kubectl apply -f k8s/nginx-configmap.yaml
```

### Step 3: Create PVCs

```bash
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/redis-pvc.yaml
```

### Step 4: Deploy Databases (wait for readiness)

```bash
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml

# Wait for postgres to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n qilema --timeout=60s

kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/redis-service.yaml

# Wait for redis to be ready
kubectl wait --for=condition=ready pod -l app=redis -n qilema --timeout=60s
```

### Step 5: Deploy Backend & Nginx

```bash
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml

kubectl apply -f k8s/nginx-deployment.yaml
kubectl apply -f k8s/nginx-service.yaml

# Wait for backend to be ready
kubectl wait --for=condition=ready pod -l app=backend -n qilema --timeout=120s
```

### Step 6: Deploy Ingress & HPA (Optional)

```bash
# Only if you set up cert-manager
kubectl apply -f k8s/ingress.yaml

# Enable autoscaling
kubectl apply -f k8s/backend-hpa.yaml
```

### Combined One-Liner Deployment

```bash
kubectl apply -f k8s/
```

## Verification

### Check Deployments

```bash
# List all resources
kubectl get all -n qilema

# Get pods and status
kubectl get pods -n qilema -o wide

# Describe backend deployment
kubectl describe deployment backend -n qilema
```

### Check Services

```bash
# List services
kubectl get svc -n qilema

# Get LoadBalancer external IP (wait for it to appear)
kubectl get svc nginx -n qilema -w
```

### Access the Application

**Via LoadBalancer:**
```bash
EXTERNAL_IP=$(kubectl get svc nginx -n qilema -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$EXTERNAL_IP/health
```

**Via kubectl port-forward:**
```bash
kubectl port-forward -n qilema svc/nginx 8080:80
curl http://localhost:8080/health
```

**View Swagger Docs:**
```bash
# Port forward backend directly
kubectl port-forward -n qilema svc/backend 8000:8000
# Open http://localhost:8000/docs
```

### Check Logs

```bash
# Backend logs
kubectl logs -n qilema deployment/backend -f

# Postgres logs
kubectl logs -n qilema deployment/postgres -f

# Redis logs
kubectl logs -n qilema deployment/redis -f

# Nginx logs
kubectl logs -n qilema deployment/nginx -f
```

### Check Pod Events

```bash
kubectl describe pod <pod-name> -n qilema
```

## Scaling & Autoscaling

### Manual Scaling

```bash
# Scale backend to 3 replicas
kubectl scale deployment backend -n qilema --replicas=3

# Scale nginx to 3 replicas
kubectl scale deployment nginx -n qilema --replicas=3
```

### View HPA Status

```bash
kubectl get hpa -n qilema

# Watch HPA in real-time
kubectl get hpa backend -n qilema -w
```

### Generate Load (Test HPA)

```bash
kubectl run -it --rm debug --image=busybox --restart=Never -n qilema -- /bin/sh -c 'while true; do wget -q -O- http://nginx/health; done'
```

## Common Issues

### Issue: Backend pods crash with "connection refused" to postgres

**Solution:** Postgres deployment not ready. Check logs:
```bash
kubectl logs -n qilema deployment/postgres
kubectl describe pod -n qilema -l app=postgres
```

Ensure postgres is healthy before backend starts:
```bash
kubectl wait --for=condition=ready pod -l app=postgres -n qilema --timeout=60s
```

### Issue: Nginx shows 502 Bad Gateway

**Solution:** Backend service not responding. Verify:
```bash
# Check backend pod status
kubectl get pods -n qilema -l app=backend

# Check backend logs
kubectl logs -n qilema -l app=backend --all-containers=true

# Test backend health directly
kubectl exec -it -n qilema deployment/nginx -- wget -O- http://backend:8000/health
```

### Issue: PVC pending forever

**Solution:** No storage class available. Check:
```bash
kubectl get storageclass

# If none exist, use local storage or install a storage provisioner (e.g., local-path)
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/deploy/local-path-storage.yaml
```

### Issue: LoadBalancer service shows `<pending>`

**Solution:** No cloud provider or load balancer available. Options:
1. Change `nginx-service.yaml` to `type: NodePort`
2. Use `kubectl port-forward`
3. Install MetalLB for bare metal: https://metallb.universe.tf/

## Secrets Management

**Never commit secrets to git.** Instead:

```bash
# Use sealed-secrets, external-secrets, or external config managers

# Example with kustomize + secretGenerator
# kustomization.yaml
secretGenerator:
- name: postgres-secret
  literals:
  - POSTGRES_PASSWORD=my-secret

# Deploy with kustomize
kubectl apply -k ./
```

## Monitoring & Logging

### Install Prometheus

```bash
kubectl apply -f https://github.com/prometheus-operator/prometheus-operator/releases/download/v0.68.0/bundle.yaml
```

### Install ELK Stack (Optional)

```bash
# Use Helm
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch -n logging --create-namespace
helm install filebeat elastic/filebeat -n logging
```

## Rollback & Updates

### Update Backend Image

```bash
kubectl set image deployment/backend backend=your-registry/qilema-backend:v1.1.0 -n qilema
```

### Check Rollout Status

```bash
kubectl rollout status deployment/backend -n qilema
```

### Rollback to Previous Version

```bash
kubectl rollout undo deployment/backend -n qilema
```

## Cleanup

### Delete Everything

```bash
kubectl delete namespace qilema
```

### Delete Specific Resource

```bash
kubectl delete deployment backend -n qilema
```

## Next Steps

1. **Monitoring:** Add Prometheus scrape targets to backend `/metrics` endpoint
2. **Persistence:** Consider backup strategies for PostgreSQL PVC
3. **HTTPS:** Configure cert-manager with Let's Encrypt
4. **CI/CD:** Integrate kubectl apply into your CI pipeline (GitHub Actions, GitLab CI, etc.)
5. **Resource Quotas:** Add namespace-level quotas in `namespace.yaml`
6. **Network Policies:** Restrict pod-to-pod communication
