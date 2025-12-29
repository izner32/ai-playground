# Cloud Monitoring - Basic Alerts for AI Agent API

# Notification channel (email)
resource "google_monitoring_notification_channel" "email" {
  display_name = "AI Agent Alerts Email"
  type         = "email"

  labels = {
    email_address = var.alert_email
  }
}

# Alert: High Error Rate (5xx errors > 5% of requests)
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "${local.service_name} - High Error Rate"
  combiner     = "OR"

  conditions {
    display_name = "Error rate > 5%"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${local.service_name}\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class=\"5xx\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "1800s"
  }

  documentation {
    content   = "High error rate detected on ${local.service_name}. Check Cloud Run logs for details."
    mime_type = "text/markdown"
  }
}

# Alert: High Latency (p95 > 5 seconds)
resource "google_monitoring_alert_policy" "high_latency" {
  display_name = "${local.service_name} - High Latency"
  combiner     = "OR"

  conditions {
    display_name = "p95 latency > 5s"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${local.service_name}\" AND metric.type=\"run.googleapis.com/request_latencies\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 5000

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_PERCENTILE_95"
        cross_series_reducer = "REDUCE_MAX"
      }

      trigger {
        count = 1
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "1800s"
  }

  documentation {
    content   = "High latency detected on ${local.service_name}. p95 latency exceeded 5 seconds."
    mime_type = "text/markdown"
  }
}

# Alert: Service Down (no requests for 5 minutes during business hours)
resource "google_monitoring_alert_policy" "service_unavailable" {
  display_name = "${local.service_name} - Service Unavailable"
  combiner     = "OR"

  conditions {
    display_name = "No successful requests"

    condition_absent {
      filter   = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${local.service_name}\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class=\"2xx\""
      duration = "300s"

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  alert_strategy {
    auto_close = "1800s"
  }

  documentation {
    content   = "No successful requests detected for ${local.service_name} in the last 5 minutes."
    mime_type = "text/markdown"
  }

  # Only enable in production
  enabled = var.environment == "prod" ? true : false
}

# Cloud Run dashboard
resource "google_monitoring_dashboard" "cloud_run" {
  dashboard_json = jsonencode({
    displayName = "${local.service_name} Dashboard"
    gridLayout = {
      columns = 2
      widgets = [
        {
          title = "Request Count"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${local.service_name}\" AND metric.type=\"run.googleapis.com/request_count\""
                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_RATE"
                  }
                }
              }
              plotType = "LINE"
            }]
          }
        },
        {
          title = "Request Latency (p50, p95, p99)"
          xyChart = {
            dataSets = [
              {
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${local.service_name}\" AND metric.type=\"run.googleapis.com/request_latencies\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_PERCENTILE_50"
                    }
                  }
                }
                plotType   = "LINE"
                legendTemplate = "p50"
              },
              {
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${local.service_name}\" AND metric.type=\"run.googleapis.com/request_latencies\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_PERCENTILE_95"
                    }
                  }
                }
                plotType   = "LINE"
                legendTemplate = "p95"
              },
              {
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${local.service_name}\" AND metric.type=\"run.googleapis.com/request_latencies\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_PERCENTILE_99"
                    }
                  }
                }
                plotType   = "LINE"
                legendTemplate = "p99"
              }
            ]
          }
        },
        {
          title = "Error Rate by Status Code"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${local.service_name}\" AND metric.type=\"run.googleapis.com/request_count\""
                  aggregation = {
                    alignmentPeriod    = "60s"
                    perSeriesAligner   = "ALIGN_RATE"
                    groupByFields      = ["metric.labels.response_code"]
                    crossSeriesReducer = "REDUCE_SUM"
                  }
                }
              }
              plotType = "STACKED_BAR"
            }]
          }
        },
        {
          title = "Instance Count"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${local.service_name}\" AND metric.type=\"run.googleapis.com/container/instance_count\""
                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_MAX"
                  }
                }
              }
              plotType = "LINE"
            }]
          }
        }
      ]
    }
  })
}
