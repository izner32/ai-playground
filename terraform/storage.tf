resource "google_storage_bucket" "ai_agent_storage" {
  name     = "${var.project_id}-${local.service_name}-storage"
  location = var.region

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type          = "SetStorageClass"
      storage_class = "NEARLINE"
    }
  }

  labels = local.labels
}

resource "google_storage_bucket_iam_member" "cloud_run_storage_access" {
  bucket = google_storage_bucket.ai_agent_storage.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_storage_bucket_iam_member" "cloud_run_storage_bucket_reader" {
  bucket = google_storage_bucket.ai_agent_storage.name
  role   = "roles/storage.legacyBucketReader"
  member = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

output "storage_bucket_name" {
  description = "GCS bucket name for storage"
  value       = google_storage_bucket.ai_agent_storage.name
}
