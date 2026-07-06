# DocOps

DocOps is a simple cloud-native document processing platform with a React frontend, a FastAPI backend, and an asynchronous Python worker. Files are uploaded to S3-compatible object storage, metadata is stored in PostgreSQL, and processing jobs flow through SQS.

## Architecture

Request path in AWS:

1. User opens the React frontend.
2. Frontend calls API Gateway.
3. AWS WAF protects API Gateway.
4. API Gateway invokes a Lambda authorizer.
5. If authorized, API Gateway forwards the request through a VPC Link to an internal ALB.
6. The ALB routes traffic to the FastAPI backend on EKS.
7. The backend stores document metadata in PostgreSQL on RDS.
8. The backend generates a pre-signed S3 upload URL and completes the upload workflow.
9. The backend sends a processing message to SQS.
10. The worker on EKS consumes the SQS message, downloads the object from S3, extracts text, and updates the database.
11. The frontend polls document status and renders `UPLOADED`, `PROCESSING`, `COMPLETED`, or `FAILED`.

## Repository layout

- `frontend/`: React + Vite UI with login placeholder, upload flow, document list, and document detail pages
- `backend/`: FastAPI API for document lifecycle, pre-signed URL generation, SQS enqueue, and status APIs
- `worker/`: Python queue consumer for document processing
- `infra/k8s/`: Kubernetes manifests for EKS deployment
- `terraform/`: AWS infrastructure as code
- `docker-compose.yml`: local development stack with Postgres, MinIO, LocalStack, backend, worker, and frontend

## Implemented APIs

- `POST /documents/init-upload`
- `POST /documents/complete-upload`
- `GET /documents`
- `GET /documents/{document_id}`
- `GET /documents/{document_id}/download-url`
- `DELETE /documents/{document_id}`
- `GET /health`

## Database model

Tables:

- `users`
- `documents`
- `processing_jobs`

`documents.status` transitions through:

- `PENDING_UPLOAD`
- `UPLOADED`
- `PROCESSING`
- `COMPLETED`
- `FAILED`

## Local development

Local development uses:

- PostgreSQL for the database
- MinIO for S3-compatible object storage
- LocalStack for SQS
- Docker Compose for orchestration

Start everything:

```bash
docker compose up --build
```

Local endpoints:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- MinIO API: `http://localhost:9000`
- MinIO console: `http://localhost:9001`
- LocalStack: `http://localhost:4566`

The compose stack bootstraps:

- the private bucket `docops-documents-local`
- the queue `docops-processing`

## Frontend behavior

The login page is a placeholder. It stores a mock identity in local storage and sends:

- `Authorization: Bearer docops:<user_id>:<email>:<name>`
- `X-User-Id`
- `X-User-Email`
- `X-User-Name`

That works locally and also matches the Lambda authorizer token format used in Terraform.

## Backend configuration

Key backend environment variables:

- `DATABASE_URL`
- `AWS_REGION`
- `AWS_S3_BUCKET`
- `AWS_S3_ENDPOINT_URL`
- `AWS_S3_PUBLIC_ENDPOINT_URL`
- `AWS_SQS_QUEUE_URL`
- `AWS_SQS_ENDPOINT_URL`
- `PRESIGNED_URL_TTL_SECONDS`
- `MAX_UPLOAD_SIZE_BYTES`
- `ALLOWED_CONTENT_TYPES`
- `AUTH_TRUST_HEADERS`
- `CORS_ALLOWED_ORIGINS`

Notes:

- No static AWS keys are required in AWS. Use IRSA for backend and worker pods.
- Local Compose uses MinIO and LocalStack credentials only for local emulation.
- File objects are stored as `documents/{user_id}/{document_id}/{original_filename}`.

## Worker behavior

The worker:

1. Polls SQS with long polling.
2. Marks the job `PROCESSING`.
3. Downloads the file from S3.
4. Extracts text from PDF or text-like files.
5. Builds a simple metadata payload and summary placeholder.
6. Marks the document `COMPLETED` or `FAILED`.

Supported content types in the starter implementation:

- `application/pdf`
- `text/plain`
- `text/markdown`
- `text/csv`
- `application/json`

## Kubernetes deployment

The `infra/k8s/` manifests deploy into namespace `docops` and include:

- frontend Deployment + Service
- backend Deployment + Service
- worker Deployment
- internal backend ALB ingress
- public frontend ALB ingress
- ConfigMap and Secret template
- IRSA-ready ServiceAccounts
- resource requests and limits
- health probes
- HPA resources

Deploy:

```bash
kubectl apply -k infra/k8s
```

Before applying:

1. Push images and replace the placeholder image names.
2. Replace placeholder subnet annotations in the ingress manifests.
3. Replace IRSA role ARNs in `infra/k8s/serviceaccounts.yaml`.
4. Replace the database URL in `infra/k8s/secret.example.yaml`.
5. Install the AWS Load Balancer Controller in the EKS cluster.

## Terraform deployment

Terraform provisions:

- VPC
- public, app-private, and DB-private subnets in at least two AZs
- EKS cluster and node group
- RDS PostgreSQL
- private S3 bucket
- SQS queue and DLQ
- IRSA roles for backend and worker
- Lambda authorizer placeholder
- API Gateway HTTP API
- VPC Link for the backend ALB
- WAF for API Gateway
- CloudWatch log groups
- optional Route53 records

Basic flow:

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

Then:

1. Deploy Kubernetes workloads.
2. Wait for the frontend and backend ALBs created by the ingress objects.
3. Fill in the generated ALB DNS and listener values in `terraform.tfvars`.
4. Re-run `terraform apply` so API Gateway and Route53 can be fully connected.

## Lambda authorizer

The placeholder Lambda authorizer accepts bearer tokens in this format:

```text
Bearer docops:<user_id>:<email>:<name>
```

On success it returns authorizer context fields:

- `x-user-id`
- `x-user-email`
- `x-user-name`

In this starter implementation the frontend also sends those headers directly. The authorizer validates the bearer token and can be extended later with API Gateway parameter mapping so the backend only consumes trusted headers from the gateway.

## Example curl commands

Set headers:

```bash
export DOCOPS_USER_ID="00000000-0000-0000-0000-000000000001"
export DOCOPS_EMAIL="demo@docops.local"
export DOCOPS_NAME="Demo User"
```

Health check:

```bash
curl http://localhost:8000/health
```

Init upload:

```bash
curl -X POST http://localhost:8000/documents/init-upload \
  -H "Content-Type: application/json" \
  -H "X-User-Id: $DOCOPS_USER_ID" \
  -H "X-User-Email: $DOCOPS_EMAIL" \
  -H "X-User-Name: $DOCOPS_NAME" \
  -d '{
    "filename": "sample.txt",
    "content_type": "text/plain",
    "size_bytes": 24
  }'
```

Upload to the returned `upload_url`:

```bash
curl -X PUT "<upload_url>" \
  -H "Content-Type: text/plain" \
  --data-binary @sample.txt
```

Complete upload:

```bash
curl -X POST http://localhost:8000/documents/complete-upload \
  -H "Content-Type: application/json" \
  -H "X-User-Id: $DOCOPS_USER_ID" \
  -H "X-User-Email: $DOCOPS_EMAIL" \
  -H "X-User-Name: $DOCOPS_NAME" \
  -d '{
    "document_id": "<document_id>"
  }'
```

List documents:

```bash
curl http://localhost:8000/documents \
  -H "X-User-Id: $DOCOPS_USER_ID" \
  -H "X-User-Email: $DOCOPS_EMAIL" \
  -H "X-User-Name: $DOCOPS_NAME"
```

Get one document:

```bash
curl http://localhost:8000/documents/<document_id> \
  -H "X-User-Id: $DOCOPS_USER_ID" \
  -H "X-User-Email: $DOCOPS_EMAIL" \
  -H "X-User-Name: $DOCOPS_NAME"
```

Get download URL:

```bash
curl http://localhost:8000/documents/<document_id>/download-url \
  -H "X-User-Id: $DOCOPS_USER_ID" \
  -H "X-User-Email: $DOCOPS_EMAIL" \
  -H "X-User-Name: $DOCOPS_NAME"
```

Delete a document:

```bash
curl -X DELETE http://localhost:8000/documents/<document_id> \
  -H "X-User-Id: $DOCOPS_USER_ID" \
  -H "X-User-Email: $DOCOPS_EMAIL" \
  -H "X-User-Name: $DOCOPS_NAME"
```

## Basic testing steps

1. Start the local stack with Docker Compose.
2. Open the frontend and log in with the default placeholder identity.
3. Upload a `.txt` or `.pdf` document.
4. Verify the backend inserts metadata into PostgreSQL.
5. Verify the worker moves the document to `PROCESSING` and then `COMPLETED`.
6. Verify the details page shows summary, extracted metadata, and extracted text.
7. Verify download works only after processing completes.

## Future extension

- Add OpenSearch indexing from the worker for full-text document search.
- Replace the mock Lambda authorizer with real JWT verification against your IdP.
- Push Kubernetes app logs to CloudWatch using Fluent Bit or the CloudWatch Observability add-on.

OpenSearch is intentionally left out of the starter path. The current worker already produces extracted text and result metadata that can be indexed later with an additional async consumer or a second worker stage.
