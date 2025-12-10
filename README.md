# AI Agent Database Query System

A GCP-based system where users interact with an AI agent that retrieves data from a database.

## Architecture

- **API Gateway**: Entry point for all requests
- **Cloud Run**: Hosts the Python API service with AI agent
- **Cloud SQL/Firestore**: Database for data storage
- **GCS**: Storage for logs, artifacts, and AI model data
- **Terraform**: Infrastructure as Code

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
- `ANTHROPIC_API_KEY` - API key for Claude (if using Anthropic)
