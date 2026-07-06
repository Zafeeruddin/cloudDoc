# DocOps Kubernetes Manifests

Apply the manifests after you have:

1. Built and pushed the three container images.
2. Installed the AWS Load Balancer Controller in the cluster.
3. Replaced placeholder values in `configmap.yaml`, `secret.example.yaml`, and `serviceaccounts.yaml`.

Key points:

- Namespace: `docops`
- Backend ingress: internal ALB for API Gateway to target
- Frontend ingress: internet-facing ALB for browser access
- Backend and worker use IRSA through `backend-sa` and `worker-sa`
- Secrets intentionally contain only the database URL; AWS access should come from IRSA
- Frontend reads `VITE_API_BASE_URL` at container start and exposes `/healthz`

Deploy:

```bash
kubectl apply -k infra/k8s
```

Useful follow-up checks:

```bash
kubectl get all -n docops
kubectl get ingress -n docops
kubectl logs deploy/backend -n docops
kubectl logs deploy/worker -n docops
```
