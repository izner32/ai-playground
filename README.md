# AI Agent Database Query System

An AI-powered API that lets users query databases using natural language. Instead of writing SQL, users ask questions in plain English and get human-readable answers.

## What It Does

```
User: "Show me the top 5 customers by total orders"

AI Agent:
1. Converts to SQL: SELECT customer_name, COUNT(*) FROM orders GROUP BY...
2. Executes query on PostgreSQL
3. Returns: "Your top 5 customers are: Acme Corp (145 orders), ..."
```

## Key Features

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
│   ├── github_wif.tf    # GitHub Actions auth (WIF)
│   └── monitoring.tf    # Alerts and dashboards
└── scripts/
    └── setup_db.sh      # Database setup script
```

## Monitoring

### Alert Policies

| Alert | Condition | Duration | Meaning |
|-------|-----------|----------|---------|
| **High Error Rate** | 5xx errors > 5% of requests | 5 minutes | 5+ out of 100 requests are encountering 5xx errors |
| **High Latency** | p95 response time > 5 seconds | 5 minutes | 5+ out of 100 requests take over 5 seconds |
| **Service Unavailable** | No 2xx responses (prod only) | 5 minutes | Service is completely down |

### Dashboard

- **Request Count** - Traffic over time
- **Request Latency** - p50, p95, p99 percentiles
- **Error Rate by Status Code** - Breakdown of HTTP responses
- **Instance Count** - Auto-scaling behavior

### Access

- Dashboard: `https://console.cloud.google.com/monitoring/dashboards`
- Alerts: `https://console.cloud.google.com/monitoring/alerting`
- Logs: `https://console.cloud.google.com/logs`

## IAM & Security

### Service Accounts

| Service Account | Purpose |
|-----------------|---------|
| `ai-agent-api-dev-sa` | Cloud Run runtime identity |
| `github-actions-sa` | CI/CD pipeline (via Workload Identity Federation) |

### Cloud Run Service Account Roles

| Role | Resource | Purpose |
|------|----------|---------|
| `roles/cloudsql.client` | Project | Connect to Cloud SQL |
| `roles/secretmanager.secretAccessor` | Secrets | Read API keys and DB password |
| `roles/storage.objectAdmin` | GCS Bucket | Read/write query logs |
| `roles/run.invoker` | Cloud Run | Allow API Gateway invocation |

### Security Practices

1. **Least Privilege** - Service accounts only have required permissions
2. **Workload Identity Federation** - No service account keys stored in GitHub
3. **Secrets in Secret Manager** - No plaintext secrets in environment variables
4. **Ingress Control** - Configurable traffic restrictions

## Documentation

See [SUMMARY.md](SUMMARY.md) for detailed documentation including:
- Quick start and deployment guide
- API reference and usage examples
- Configuration options
- Troubleshooting guide
- CI/CD setup
- Local development

## License

MIT
