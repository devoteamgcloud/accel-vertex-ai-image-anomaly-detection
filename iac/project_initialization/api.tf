# Google services API
resource "google_project_service" "service_usage_api" {
  service                    = "serviceusage.googleapis.com"
  disable_dependent_services = true
  project                    = var.project_id
  disable_on_destroy         = false
}
resource "google_project_service" "artifactregistry_api" {
  service                    = "artifactregistry.googleapis.com"
  disable_on_destroy         = false
  disable_dependent_services = true
  project                    = var.project_id
  depends_on = [
    google_project_service.service_usage_api
  ]
}
resource "google_project_service" "billing_api" {
  service                    = "cloudbilling.googleapis.com"
  disable_on_destroy         = false
  disable_dependent_services = true
  project                    = var.project_id
  depends_on = [
    google_project_service.service_usage_api
  ]
}
resource "google_project_service" "cloud_resource_manager_api" {
  service                    = "cloudresourcemanager.googleapis.com"
  disable_dependent_services = true
  disable_on_destroy         = false
  project                    = var.project_id
  depends_on                 = [google_project_service.billing_api]
}
resource "google_project_service" "bigquery_api" {
  service                    = "bigquery.googleapis.com"
  disable_dependent_services = true
  disable_on_destroy         = false
  project                    = var.project_id
  depends_on                 = [google_project_service.billing_api]
}
resource "google_project_service" "cloudbuild_api" {
  project                    = var.project_id
  service                    = "cloudbuild.googleapis.com"
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on                 = [google_project_service.billing_api]
}
resource "google_project_service" "cloudfunctions_api" {
  project                    = var.project_id
  service                    = "cloudfunctions.googleapis.com"
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on                 = [google_project_service.billing_api]
}
resource "google_project_service" "cloudrun_api" {
  project                    = var.project_id
  service                    = "run.googleapis.com"
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on                 = [google_project_service.billing_api]
}
resource "google_project_service" "compute_api" {
  project                    = var.project_id
  service                    = "compute.googleapis.com"
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on                 = [google_project_service.billing_api]
}
resource "google_project_service" "ai_platform" {
  project                    = var.project_id
  service                    = "aiplatform.googleapis.com"
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on                 = [google_project_service.billing_api]
}
resource "google_project_service" "notebooks" {
  project                    = var.project_id
  service                    = "notebooks.googleapis.com"
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on                 = [google_project_service.billing_api]
}
resource "google_project_service" "ml" {
  project                    = var.project_id
  service                    = "ml.googleapis.com"
  disable_on_destroy         = false
  disable_dependent_services = true
  depends_on                 = [google_project_service.billing_api]
}

data "google_project" "project" {
  depends_on = [google_project_service.cloud_resource_manager_api]
}

resource "null_resource" "api_propagation" {
  provisioner "local-exec" {
    command = "sleep 120"
  }
  depends_on = [
    google_project_service.artifactregistry_api,
    google_project_service.billing_api,
    google_project_service.cloud_resource_manager_api,
    google_project_service.bigquery_api,
    google_project_service.cloudbuild_api,
    google_project_service.cloudfunctions_api,
    google_project_service.cloudrun_api,
    google_project_service.compute_api,
    google_project_service.ai_platform,
    google_project_service.notebooks,
    google_project_service.ml,
  ]
}
