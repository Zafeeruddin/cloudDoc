# Terraform

This directory provisions the AWS foundation for DocOps:

- VPC with separate public, app-private, and DB-private subnets across 2 AZs
- EKS cluster and managed node group
- EKS CloudWatch Observability add-on
- Private S3 bucket for uploaded documents
- SQS queue and DLQ for asynchronous processing
- RDS PostgreSQL in private DB subnets
- IRSA roles for the backend and worker
- API Gateway HTTP API, Lambda authorizer, VPC Link, and WAF
- CloudWatch log groups
- Optional Route53 placeholder records

## Apply order

1. Initialize and apply the base infrastructure:

```bash
terraform init
terraform apply -var="db_password=replace-me"
```

2. Build and push the frontend, backend, and worker images.
3. Deploy the Kubernetes manifests from `infra/k8s/`.
4. Wait for the backend ingress to create its internal ALB through the AWS Load Balancer Controller.
5. Capture the backend ALB listener ARN.
6. Re-apply Terraform with that ARN so API Gateway can forward traffic through the VPC Link:

```bash
terraform apply \
  -var="db_password=replace-me" \
  -var="backend_alb_listener_arn=arn:aws:elasticloadbalancing:us-east-1:123456789012:listener/app/..."
```

7. If you want DNS placeholders created, also set:

- `route53_zone_id`
- `api_record_name`
- `frontend_record_name`
- `frontend_alias_target`

## Notes

- The backend and worker should use the IRSA role ARNs output by Terraform in the Kubernetes service account annotations.
- The backend ingress is designed to stay internal so API Gateway is the public API entry point.
- AWS Load Balancer Controller installation is intentionally left as an operator step.
- S3 blocks public access and uses server-side encryption.
- RDS is private and not publicly accessible.
