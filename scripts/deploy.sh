#!/bin/bash

set -e

# Get the script's directory and project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

PROJECT_ID=${GCP_PROJECT_ID:-$(gcloud config get-value project)}
REGION=${REGION:-"us-central1"}
SERVICE_NAME=${SERVICE_NAME:-"ai-agent-api-dev"}

echo "====================================="
echo "AI Agent API Deployment Script"
echo "====================================="
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo "====================================="

if [ -z "$PROJECT_ID" ]; then
    echo "Error: GCP_PROJECT_ID is not set"
    echo "Set it with: export GCP_PROJECT_ID=your-project-id"
    exit 1
fi

echo "Step 1: Building Docker image..."
cd "$PROJECT_ROOT/api"

IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
echo "Building image: $IMAGE_NAME"

gcloud builds submit --tag "$IMAGE_NAME" --project "$PROJECT_ID"

echo "Step 2: Deploying to Cloud Run..."
cd "$PROJECT_ROOT/terraform"

if [ ! -f "terraform.tfvars" ]; then
    echo "Error: terraform.tfvars not found"
    echo "Copy terraform.tfvars.example and fill in your values"
    exit 1
fi

terraform init

terraform plan \
    -var="project_id=$PROJECT_ID" \
    -var="container_image=$IMAGE_NAME" \
    -out=tfplan

echo ""
echo "Review the plan above. Do you want to apply? (yes/no)"
read -r APPLY_CONFIRM

if [ "$APPLY_CONFIRM" = "yes" ]; then
    terraform apply tfplan

    echo ""
    echo "====================================="
    echo "Deployment completed!"
    echo "====================================="

    API_GATEWAY_URL=$(terraform output -raw api_gateway_endpoint 2>/dev/null || echo "N/A")

    echo "API Gateway URL: $API_GATEWAY_URL"
    echo ""
    echo "Test with:"
    echo "curl -X POST $API_GATEWAY_URL/query \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"query\": \"Show me all records\"}'"
else
    echo "Deployment cancelled"
    rm tfplan
    exit 0
fi
