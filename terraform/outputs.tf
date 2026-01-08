output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "api_gateway_endpoint" {
  description = "API Gateway endpoint URL"
  value       = "https://${google_api_gateway_gateway.gateway.default_hostname}"
}

output "cloud_run_service_url" {
  description = "Cloud Run service URL (internal)"
  value       = google_cloud_run_v2_service.api.uri
}

output "database_connection_string" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.main.connection_name
  sensitive   = true
}

output "storage_bucket" {
  description = "GCS storage bucket name"
  value       = google_storage_bucket.ai_agent_storage.name
}

output "service_account_email" {
  description = "Service account email"
  value       = google_service_account.cloud_run_sa.email
}

output "deployment_instructions" {
  description = "Next steps for deployment"
  value       = <<-EOT
    Deployment Complete!

    API Gateway Endpoint: https://${google_api_gateway_gateway.gateway.default_hostname}

    Next steps:
    1. Build and push Docker image:
       cd api
       gcloud builds submit --tag gcr.io/${var.project_id}/${local.service_name}

    2. Update Cloud Run service:
       gcloud run services update ${local.service_name} \
         --image gcr.io/${var.project_id}/${local.service_name} \
         --region ${var.region}

    3. Test the API:
       curl -X POST https://${google_api_gateway_gateway.gateway.default_hostname}/query \
         -H "Content-Type: application/json" \
         -d '{"query": "Show me all records"}'
  EOT
}
