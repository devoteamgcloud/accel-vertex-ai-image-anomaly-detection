locals {
  artifact_registry_repositories = {
    "pipeline-containers" = {
      location    = var.artifact_location
      description = "Repository containing Devoteam G Cloud's pipeline Docker containers."
      format      = "DOCKER"
    }
    "pipeline-packages" = {
      location    = var.artifact_location
      description = "Repository containing Devoteam G Cloud's pipeline Python packages."
      format      = "PYTHON"
    }
  }

  cloud_build_substitutions = merge(
    { for pipeline_name, config in var.pipelines : pipeline_name => merge(config.cloud_build["substitutions"], {
      "_PIPELINE_BUCKET"        = var.pipeline_bucket
      "_PIPELINE_NAME"          = pipeline_name
      "_PROJECT_ID"             = var.project_id
      "_REGION"                 = var.region
      "_PIPELINE_SA"            = "${var.pipeline_service_account_name}@${var.project_id}.iam.gserviceaccount.com"
      "_MODEL_BUCKET"           = var.model_bucket
      "_ARTIFACT_REGISTRY_URL"  = "${var.artifact_location}-docker.pkg.dev/${var.project_id}/pipeline-containers"
      "_ARTIFACT_REGISTRY_URL_PACKAGE" = "https://${var.artifact_location}-python.pkg.dev/${var.project_id}/pipeline-packages/"
      "_CONTAINER_REGISTRY_URL" = "gcr.io/${var.project_id}"
    }) }
  )
}
