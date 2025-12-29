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

- Natural language to SQL conversion (powered by Gemini 2.5 Flash)
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
| Gemini | Natural language ↔ SQL conversion |
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
- Google Gemini API key

### Deploy

```bash
# 1. Configure GCP
export GCP_PROJECT_ID="your-project-id"
gcloud config set project $GCP_PROJECT_ID

# 2. Set up Terraform
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# 3. Deploy
terraform init
terraform apply

# 4. Build and deploy the API
cd ..
./scripts/deploy.sh
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check (DB + storage status) |
| `/query` | POST | Send natural language query |
| `/queries/{id}` | GET | Retrieve past query result |

### Example Request

```bash
curl -X POST $API_URL/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me all users", "user_id": "user123"}'
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GCP_PROJECT_ID` | GCP project ID |
| `GOOGLE_API_KEY` | Google Gemini API key |
| `DB_TYPE` | `cloudsql` or `postgres` |
| `CLOUD_SQL_INSTANCE` | Cloud SQL connection name |
| `DB_NAME` | Database name |
| `DB_USER` | Database user |
| `DB_PASS` | Database password |
| `GCS_BUCKET` | GCS bucket for logs |
| `LOG_LEVEL` | Logging level (default: INFO) |

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

## Monitoring

Cloud Monitoring is configured with:

- **Alerts**: High error rate, high latency, service unavailable
- **Dashboard**: Request count, latency percentiles, error rates, instance count

View logs:
```bash
gcloud logging read "resource.type=cloud_run_revision" --limit 50
```

## License

MIT
