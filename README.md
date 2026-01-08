# AI Agent Database Query System

An AI-powered API that lets users query databases using natural language. Instead of writing SQL, users ask questions in plain English and get human-readable answers.

## What It Does

**Example:**

```
User: "Show me the top 5 customers by total orders"

AI Agent:
1. Converts to SQL: SELECT customer_name, COUNT(*) FROM orders GROUP BY...
2. Executes query on PostgreSQL
3. Returns: "Your top 5 customers are: Acme Corp (145 orders), ..."
```

**Key Features:**

- Natural language to SQL conversion (powered by Gemini 2.0 Flash)
- Automatic response formatting - raw data becomes readable answers
- Query logging for audit trails
- Read-only queries (SELECT only) for safety
- Structured JSON logging with request tracing
- Cloud Monitoring alerts and dashboards

## Architecture

```
User ──▶ API Gateway ──▶ Cloud Run (FastAPI + AI Agent) ──▶ Cloud SQL
                                      │                         │
                                      ▼                         ▼
                                   Gemini ◀───────────── Query Results
                                      │
                                      ▼
                              Response ──▶ GCS (logs)
```

| Component | Description |
|-----------|-------------|
| API Gateway | HTTPS entry point with rate limiting |
| Cloud Run | FastAPI + AI Agent (serverless, auto-scaling) |
| Cloud SQL | PostgreSQL database |
| GCS | Query logs storage |
| Gemini | Natural language to SQL conversion |
| Cloud Monitoring | Alerts, dashboards, and metrics |

## Project Structure

```
.
├── .github/workflows/     # CI/CD pipelines
│   ├── ci.yml            # Lint, test, validate
│   └── deploy.yml        # Deploy to GCP
├── api/                   # Python API service
│   ├── app.py            # Main FastAPI application
│   ├── ai_agent.py       # AI agent logic (Gemini)
│   ├── database.py       # Database integration
│   ├── logging_config.py # Structured logging
│   ├── middleware.py     # Request tracing
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Container image
├── terraform/            # Infrastructure as Code
│   ├── main.tf          # Provider and APIs
│   ├── variables.tf     # Variable definitions
│   ├── cloud_run.tf     # Cloud Run config
│   ├── database.tf      # Cloud SQL config
│   ├── api_gateway.tf   # API Gateway config
│   ├── storage.tf       # GCS bucket config
│   └── monitoring.tf    # Alerts and dashboards
└── scripts/
    └── deploy.sh        # Manual deployment script
```

## Quick Start

### Prerequisites

- GCP account with billing enabled
- `gcloud` CLI installed and authenticated
- Terraform >= 1.0
- Google Gemini API key (from [Google AI Studio](https://aistudio.google.com/apikey))

### Deploy

```bash
# 1. Configure GCP
export GCP_PROJECT_ID="your-project-id"
gcloud config set project $GCP_PROJECT_ID

# 2. Set up Terraform
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# 3. Deploy infrastructure
terraform init
terraform apply

# 4. Build and deploy the API
cd ../api
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/ai-agent-api-dev

# 5. Update Cloud Run with your image
gcloud run services update ai-agent-api-dev \
  --image gcr.io/$GCP_PROJECT_ID/ai-agent-api-dev \
  --region us-central1
```

## API Reference

### Base URL

```
https://ai-agent-api-dev-gw-XXXXXX.uc.gateway.dev
```

Get your actual URL from Terraform output:
```bash
cd terraform && terraform output api_gateway_endpoint
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check (DB + storage status) |
| `/query` | POST | Send natural language query |
| `/queries/{id}` | GET | Retrieve past query result |

### Using with cURL

**Health Check:**
```bash
curl https://your-api-gateway-url.uc.gateway.dev/health
```

**Query Endpoint:**
```bash
curl -X POST https://your-api-gateway-url.uc.gateway.dev/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me all users", "user_id": "user123"}'
```

### Using with Postman

1. **Create a new request**
   - Method: `POST`
   - URL: `https://your-api-gateway-url.uc.gateway.dev/query`

2. **Headers tab**
   ```
   Content-Type: application/json
   ```

3. **Body tab**
   - Select `raw` and `JSON`
   - Enter:
   ```json
   {
     "query": "Show me all records",
     "user_id": "optional-user-id",
     "context": {
       "optional": "additional context"
     }
   }
   ```

4. **Click Send**

### Response Format

**Success (200):**
```json
{
  "query_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-01-05T12:00:00Z",
  "response": "Here are the top 5 customers by orders...",
  "data": {
    "results": [...],
    "count": 5,
    "sql_query": "SELECT * FROM customers ORDER BY orders DESC LIMIT 5"
  }
}
```

**Error (4xx/5xx):**
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Configuration

### Terraform Variables (terraform.tfvars)

| Variable | Description | Example |
|----------|-------------|---------|
| `project_id` | GCP project ID | `my-project-123` |
| `region` | GCP region | `us-central1` |
| `environment` | Environment name | `dev`, `prod` |
| `service_name` | Service name prefix | `ai-agent-api` |
| `google_api_key` | Gemini API key | `AIzaSy...` |
| `container_image` | Container image URL | `gcr.io/project/image` |
| `min_instances` | Minimum Cloud Run instances | `0` |
| `max_instances` | Maximum Cloud Run instances | `10` |
| `alert_email` | Email for alerts (optional) | `alerts@example.com` |

### Environment Variables (Cloud Run)

| Variable | Description |
|----------|-------------|
| `GCP_PROJECT_ID` | GCP project ID |
| `GOOGLE_API_KEY` | Google Gemini API key (from Secret Manager) |
| `DB_TYPE` | `cloudsql` or `postgres` |
| `CLOUD_SQL_INSTANCE` | Cloud SQL connection name |
| `DB_NAME` | Database name |
| `DB_USER` | Database user |
| `DB_PASS` | Database password (from Secret Manager) |
| `GCS_BUCKET` | GCS bucket for logs |

## Monitoring

### Alert Policies

The following alerts are configured automatically:

| Alert | Condition | Duration |
|-------|-----------|----------|
| **High Error Rate** | 5xx errors > 5% of requests | 5 minutes |
| **High Latency** | p95 response time > 5 seconds | 5 minutes |
| **Service Unavailable** | No 2xx responses (prod only) | 5 minutes |

### Dashboard

A monitoring dashboard is created with:
- **Request Count** - Traffic over time
- **Request Latency** - p50, p95, p99 percentiles
- **Error Rate by Status Code** - Breakdown of HTTP responses
- **Instance Count** - Auto-scaling behavior

### Accessing Monitoring

**GCP Console:**
- Dashboard: https://console.cloud.google.com/monitoring/dashboards?project=YOUR_PROJECT_ID
- Alerts: https://console.cloud.google.com/monitoring/alerting?project=YOUR_PROJECT_ID
- Logs: https://console.cloud.google.com/logs?project=YOUR_PROJECT_ID

**CLI:**
```bash
# View recent logs
gcloud logging read 'resource.type="cloud_run_revision" AND resource.labels.service_name="ai-agent-api-dev"' --limit=20

# List alert policies
gcloud alpha monitoring policies list

# Check service status
gcloud run services describe ai-agent-api-dev --region=us-central1
```

### Enable Email Notifications

Add to `terraform.tfvars`:
```hcl
alert_email = "your-email@example.com"
```

Then run `terraform apply`.

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `405 Method Not Allowed` | Wrong HTTP method or endpoint | Use `POST` for `/query`, `GET` for `/health` |
| `404 Not Found` | Ingress settings blocking traffic | Set `ingress = "INGRESS_TRAFFIC_ALL"` in cloud_run.tf |
| `429 RESOURCE_EXHAUSTED` | Gemini API quota exceeded | Wait for quota reset or upgrade to paid tier |
| `403 Permission Denied` | Missing IAM permissions | Check service account has required roles |
| Secret version error | Old secret destroyed before new one created | Add `create_before_destroy = true` lifecycle |

### Checking Logs

```bash
# Cloud Run logs
gcloud logging read 'resource.type="cloud_run_revision"' --limit=20 --format="table(timestamp,jsonPayload.message)"

# API Gateway logs
gcloud logging read 'resource.type="apigateway.googleapis.com/Gateway"' --limit=10

# Filter by severity
gcloud logging read 'resource.type="cloud_run_revision" AND severity>=ERROR' --limit=10
```

### Verifying Deployment

```bash
# Check Cloud Run service status
gcloud run services describe ai-agent-api-dev --region=us-central1

# Check current container image
gcloud run services describe ai-agent-api-dev --region=us-central1 --format="value(spec.template.spec.containers[0].image)"

# List revisions
gcloud run revisions list --service=ai-agent-api-dev --region=us-central1
```

### Terraform State Issues

```bash
# If resources were modified outside Terraform (ClickOps)
terraform refresh
terraform plan  # Check for drift

# Import existing resource
terraform import google_cloud_run_v2_service.api projects/PROJECT/locations/REGION/services/SERVICE

# Remove resource from state (keeps resource, Terraform forgets it)
terraform state rm google_resource.name
```

## CI/CD

GitHub Actions workflows are configured for:

- **CI** (`ci.yml`): Runs on every push/PR
  - Python linting (Ruff)
  - Terraform validation
  - Docker build test

- **CD** (`deploy.yml`): Runs on push to main
  - Builds and pushes Docker image
  - Runs Terraform apply
  - Outputs deployment URL

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `GCP_PROJECT_ID` | GCP project ID |
| `GOOGLE_API_KEY` | Gemini API key |
| `WIF_PROVIDER` | Workload Identity Federation provider |
| `WIF_SERVICE_ACCOUNT` | GCP service account |

## IAM & Security

### Service Account

A dedicated service account is created for Cloud Run with the principle of least privilege:

```
ai-agent-api-dev-sa@PROJECT_ID.iam.gserviceaccount.com
```

### IAM Roles

| Role | Resource | Purpose |
|------|----------|---------|
| `roles/cloudsql.client` | Project | Connect to Cloud SQL database |
| `roles/secretmanager.secretAccessor` | DB Password Secret | Read database password |
| `roles/secretmanager.secretAccessor` | API Key Secret | Read Gemini API key |
| `roles/storage.objectAdmin` | GCS Bucket | Read/write query logs |
| `roles/storage.legacyBucketReader` | GCS Bucket | List bucket contents |
| `roles/run.invoker` | Cloud Run Service | Allow API Gateway to invoke |

### IAM Bindings in Terraform

```hcl
# cloud_run.tf - Service account and core permissions
google_service_account.cloud_run_sa           # Service account creation
google_project_iam_member.cloud_run_sql_client # Cloud SQL access
google_secret_manager_secret_iam_member.google_key_access # API key access
google_cloud_run_service_iam_member.invoker   # Allow invocation

# database.tf - Database secret access
google_secret_manager_secret_iam_member.cloud_run_secret_access # DB password

# storage.tf - Storage permissions
google_storage_bucket_iam_member.cloud_run_storage_access # Object admin
google_storage_bucket_iam_member.cloud_run_storage_bucket_reader # Bucket read
```

### Security Best Practices

1. **Least Privilege** - Service account only has permissions it needs
2. **No User Credentials** - Cloud Run uses service account identity
3. **Secrets in Secret Manager** - No plaintext secrets in environment variables
4. **Ingress Control** - Configure `ingress` setting in cloud_run.tf:
   - `INGRESS_TRAFFIC_ALL` - Public access (current)
   - `INGRESS_TRAFFIC_INTERNAL_ONLY` - VPC only
   - `INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER` - Internal LB only

### Viewing IAM Permissions

```bash
# List service account roles
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:ai-agent-api-dev-sa@" \
  --format="table(bindings.role)"

# Check specific resource permissions
gcloud storage buckets get-iam-policy gs://BUCKET_NAME
gcloud secrets get-iam-policy SECRET_NAME
```

### Adding New Permissions

If your app needs additional GCP services, add IAM bindings in Terraform:

```hcl
# Example: Add BigQuery access
resource "google_project_iam_member" "bigquery_access" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}
```

## Infrastructure as Code Best Practices

### Avoid ClickOps

All infrastructure changes should go through Terraform:

1. **Don't modify resources in GCP Console** - Terraform will revert changes on next apply
2. **Use CI/CD pipeline** - Changes go through PR review
3. **If you must use ClickOps** - Import the resource into Terraform state

### Secret Management

- Secrets are stored in Google Secret Manager
- Cloud Run accesses secrets via environment variables
- Never commit secrets to git (use `.gitignore`)

### Updating Secrets

```bash
# Update API key in terraform.tfvars, then:
terraform apply

# Force Cloud Run to pick up new secret
gcloud run services update ai-agent-api-dev --region=us-central1
```

## Local Development

```bash
cd api

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your values

# Run locally
uvicorn app:app --reload --port 8080
```

## License

MIT
