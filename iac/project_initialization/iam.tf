# Vertex AI - set up service account
resource "google_service_account" "sa-vertex-pipeline" {
  project    = var.project_id
  account_id = var.pipeline_service_account_name
  depends_on = [google_project_service.billing_api]
}

resource "google_project_iam_member" "sa-vertex-pipeline" {
  for_each = toset([
    "roles/aiplatform.admin",
    "roles/aiplatform.customCodeServiceAgent",
    "roles/aiplatform.serviceAgent",
    "roles/artifactregistry.admin",
    "roles/bigquery.dataOwner",
    "roles/datastore.user",
    "roles/ml.developer",
    "roles/ml.serviceAgent",
    "roles/storage.admin",
  ])
  project    = var.project_id
  role       = each.value
  member     = "serviceAccount:${google_service_account.sa-vertex-pipeline.email}"
  depends_on = [google_service_account.sa-vertex-pipeline]
}

resource "google_service_account_iam_member" "sa-vertex-pipeline-users" {
  for_each           = toset(var.pipeline_service_account_users)
  service_account_id = google_service_account.sa-vertex-pipeline.id
  role               = "roles/iam.serviceAccountUser"
  member             = "user:${each.value}"
}

# Cloud Build - grant additional permissions
resource "google_project_iam_member" "cloud-build" {
  for_each = toset([
    "roles/editor",
    "roles/appengine.appAdmin",
    "roles/cloudbuild.builds.editor",
    "roles/run.admin",
    "roles/storage.admin",
    "roles/storage.objectAdmin",
  ])
  project    = var.project_id
  role       = each.value
  member     = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
  depends_on = [google_project_service.cloud_resource_manager_api]
}
