terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }

  # OPTIONAL: Uncomment for remote state storage (recommended for teams)
  # backend "gcs" {
  #   # Configure with: terraform init -backend-config="bucket=your-tf-state-bucket"
  #   prefix = "terraform/state"
  # }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

locals {
  service_name = "${var.service_name}-${var.environment}"
  labels = {
    environment = var.environment
    managed_by  = "terraform"
    application = "ai-agent"
  }
}

resource "random_id" "db_name_suffix" {
  byte_length = 4
}

resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "apigateway.googleapis.com",
    "servicecontrol.googleapis.com",
    "servicemanagement.googleapis.com",
    "storage.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "vpcaccess.googleapis.com",
    "secretmanager.googleapis.com",
    "generativelanguage.googleapis.com"
  ])

  service            = each.key
  disable_on_destroy = false
}
