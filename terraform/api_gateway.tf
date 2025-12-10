resource "google_api_gateway_api" "api" {
  provider = google-beta
  api_id   = "${local.service_name}-gateway"

  depends_on = [google_project_service.required_apis]
}

resource "google_api_gateway_api_config" "api_config" {
  provider      = google-beta
  api           = google_api_gateway_api.api.api_id
  api_config_id = "${local.service_name}-config-v1"

  openapi_documents {
    document {
      path = "openapi.yaml"
      contents = base64encode(templatefile("${path.module}/openapi.yaml.tpl", {
        cloud_run_url = google_cloud_run_v2_service.api.uri
        service_account = google_service_account.cloud_run_sa.email
      }))
    }
  }

  gateway_config {
    backend_config {
      google_service_account = google_service_account.cloud_run_sa.email
    }
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [google_cloud_run_v2_service.api]
}

resource "google_api_gateway_gateway" "gateway" {
  provider   = google-beta
  api_config = google_api_gateway_api_config.api_config.id
  gateway_id = "${local.service_name}-gw"
  region     = var.region

  depends_on = [google_api_gateway_api_config.api_config]
}

output "api_gateway_url" {
  description = "API Gateway URL"
  value       = google_api_gateway_gateway.gateway.default_hostname
}
