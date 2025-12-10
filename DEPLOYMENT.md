# Deployment Guide

This guide walks you through deploying the AI Agent Database Query system to GCP.

## Prerequisites

- GCP account with billing enabled
- `gcloud` CLI installed and authenticated
- Terraform installed (version >= 1.0)
- Docker installed (for local testing)
- Anthropic API key

## Quick Start

### 1. Setup GCP Project

```bash
export GCP_PROJECT_ID="your-project-id"
gcloud config set project $GCP_PROJECT_ID
gcloud auth application-default login
```

### 2. Create GCS Bucket for Terraform State
This is optional. Terraform state tracks what infrastructure exists. Without it, Terraform doesn't know what it created. By default, Terraform stores state locally in terraform.tfstate file. This is problematic because: if you lose the file, terraform loses track of your infrastructure. second is, multiple people can't collaborate (they'd overwrite each other's terraform.tfstate).

```bash
gsutil mb -p $GCP_PROJECT_ID -l us-central1 gs://${GCP_PROJECT_ID}-terraform-state
gsutil versioning set on gs://${GCP_PROJECT_ID}-terraform-state
```

If you won't proceed with the command above (which is create gcs bucket for terraform state) then comment out these lines of codes in main.tf

```tf
backend "gcs" {
  # Configure with: terraform init -backend-config="bucket=your-tf-state-bucket"
  prefix = "terraform/state"
}
```

### 3. Configure Terraform Variables

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:
- `project_id`: Your GCP project ID
- `anthropic_api_key`: Your Anthropic API key
- Adjust other variables as needed

### 4. Initialize Terraform Backend

```bash
terraform init -backend-config="bucket=${GCP_PROJECT_ID}-terraform-state"
```

### 5. Deploy Infrastructure

```bash
terraform plan
terraform apply
```

This will create:
- Cloud SQL PostgreSQL instance
- Cloud Run service
- API Gateway
- GCS storage bucket
- Service accounts and IAM bindings
- Secret Manager secrets

### 6. Build and Deploy Application

Using the deployment script:

```bash
cd ..
export GCP_PROJECT_ID="your-project-id"
./scripts/deploy.sh
```

Or manually:

```bash
cd api
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/ai-agent-api-dev

cd ../terraform
terraform apply -var="container_image=gcr.io/$GCP_PROJECT_ID/ai-agent-api-dev"
```

### 7. Setup Database Schema

```bash
export DB_INSTANCE_NAME=$(cd terraform && terraform output -raw database_instance_name)
./scripts/setup_db.sh
```

### 8. Test the API

Get the API Gateway URL:

```bash
cd terraform
terraform output api_gateway_endpoint
```

Test the health endpoint:

```bash
API_URL=$(cd terraform && terraform output -raw api_gateway_endpoint)
curl $API_URL/health
```

Test a query:

```bash
curl -X POST $API_URL/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me all users who logged in recently",
    "user_id": "test_user"
  }'
```

## Architecture Overview

```
User Request
    |
    v
API Gateway (HTTPS endpoint)
    |
    v
Cloud Run (Python FastAPI)
    |
    +-- AI Agent (Claude)
    |       |
    |       +-- Generate SQL
    |       +-- Format Response
    |
    +-- Cloud SQL (PostgreSQL)
    |
    +-- GCS (Query logs & artifacts)
```

## Local Development

### Run Locally with Docker

```bash
cd api
docker build -t ai-agent-api .
docker run -p 8080:8080 \
  -e DATABASE_URL="postgresql://user:pass@host/db" \
  -e ANTHROPIC_API_KEY="your-key" \
  -e GCS_BUCKET="your-bucket" \
  ai-agent-api
```

### Run Locally with Python

```bash
cd api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your credentials

python app.py
```

Visit http://localhost:8080

## Monitoring and Logs

### View Cloud Run Logs

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=ai-agent-api-dev" \
  --limit 50 \
  --format json
```

### View API Gateway Logs

```bash
gcloud logging read "resource.type=api" \
  --limit 50 \
  --format json
```

### Check Cloud SQL Performance

```bash
gcloud sql operations list --instance=INSTANCE_NAME
```

## Security Best Practices

1. **API Gateway**: Configure authentication (API keys, OAuth, etc.)
2. **Cloud Run**: Use VPC connectors for private networking
3. **Database**: Enable SSL, use private IP
4. **Secrets**: Store all sensitive data in Secret Manager
5. **IAM**: Follow principle of least privilege

## Cost Optimization

- Set `min_instances = 0` to scale to zero
- Use `db-f1-micro` for development
- Enable Cloud SQL automatic backups
- Set GCS lifecycle policies for old logs

## Troubleshooting

### Cloud Run fails to start

Check logs:
```bash
gcloud run services logs read ai-agent-api-dev --region us-central1
```

### Database connection issues

Test connection:
```bash
gcloud sql connect INSTANCE_NAME --user=postgres
```

### API Gateway returns 502

Verify Cloud Run is healthy:
```bash
gcloud run services describe ai-agent-api-dev --region us-central1
```

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy
```

Delete the storage bucket:
```bash
gsutil -m rm -r gs://${GCP_PROJECT_ID}-ai-agent-api-dev-storage
gsutil -m rm -r gs://${GCP_PROJECT_ID}-terraform-state
```
