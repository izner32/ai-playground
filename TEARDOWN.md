# Teardown Guide

Complete cleanup to eliminate all GCP costs from this project.

## Steps

### 1. Destroy Terraform-managed resources

```bash
cd terraform
terraform destroy
```

Type `yes` when prompted. This deletes:
- Cloud Run service
- Cloud SQL database
- API Gateway
- GCS bucket (query logs)
- Secret Manager secrets
- Service accounts
- Workload Identity Federation
- Artifact Registry
- Monitoring dashboard and alerts

### 2. Delete the Terraform state bucket

The state bucket is protected from `terraform destroy`. Delete it manually:

```bash
gcloud storage buckets delete gs://YOUR_PROJECT_ID-terraform-state
```

Or via GCP Console: **Storage** > **Buckets** > delete `*-terraform-state`

## Optional Cleanup

### Delete Gemini API key

The API key doesn't cost anything to exist (you only pay per API call), but if you want to revoke it:

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Delete the key

### Remove GitHub secrets

If you no longer need the CI/CD pipeline:

1. Go to your repo **Settings** > **Secrets and variables** > **Actions**
2. Delete: `GCP_PROJECT_ID`, `GOOGLE_API_KEY`, `WIF_PROVIDER`, `WIF_SERVICE_ACCOUNT`
