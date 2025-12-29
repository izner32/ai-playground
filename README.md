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

- Natural language to SQL conversion (powered by Gemini)
- Automatic response formatting - raw data becomes readable answers
- Query logging for audit trails
- Read-only queries (SELECT only) for safety

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

- **API Gateway**: HTTPS entry point
- **Cloud Run**: FastAPI + AI Agent (serverless)
- **Cloud SQL**: PostgreSQL database
- **GCS**: Query logs storage
- **GCR**: Store docker container build for the api or backend 
- **Gemini**: Natural language ↔ SQL conversion

## Project Structure

```
.
├── api/                    # Python API service
│   ├── app.py             # Main FastAPI application
│   ├── ai_agent.py        # AI agent logic
│   ├── database.py        # Database integration
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Container image
├── terraform/             # Infrastructure code
│   ├── main.tf           # Main configuration
│   ├── variables.tf      # Variable definitions
│   ├── api_gateway.tf    # API Gateway config
│   ├── cloud_run.tf      # Cloud Run config
│   ├── database.tf       # Database config
│   └── storage.tf        # GCS bucket config
└── scripts/               # Deployment scripts
    └── deploy.sh         # Deployment automation
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r api/requirements.txt
   ```

2. Configure GCP credentials:
   ```bash
   gcloud auth application-default login
   ```

3. Deploy infrastructure:
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

## API Endpoints

- `POST /query` - Send query to AI agent
- `GET /health` - Health check

## Environment Variables

- `GCP_PROJECT_ID` - GCP project ID
- `DATABASE_URL` - Database connection string
- `GCS_BUCKET` - GCS bucket name
- `GOOGLE_API_KEY` - API key for Google Gemini
