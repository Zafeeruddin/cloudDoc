# Kubernetes Manifests

These manifests deploy DocOps into the `docops` namespace with separate Deployments for the frontend, backend, and worker.

## Notes

- Replace placeholder image names with your published images.
- Replace `subnet-*` placeholders with the public and private subnets created by Terraform.
- Set the IRSA role annotations on `backend-sa` and `worker-sa` to the IAM roles created for S3/SQS access.
- The backend ingress is intentionally `internal` so API Gateway can target the ALB through a VPC Link.
- The frontend ingress is public so users can reach the React app directly through Route53.
- Apply the namespace, config, secret, service account, deployment, service, ingress, and HPA manifests in that order.
