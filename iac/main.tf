provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

module "project_initialization" {
  source                         = "./project_initialization"
  project_id                     = var.project_id
  region                         = var.region
  pipeline_bucket                = var.pipeline_bucket
  model_bucket                   = var.model_bucket
  pipeline_service_account_name  = var.pipeline_service_account_name
  pipeline_service_account_users = var.pipeline_service_account_users
}

module "artifact_registry" {
  for_each = local.artifact_registry_repositories

  source = "./artifact_registry"

  description   = each.value.description
  format        = each.value.format
  location      = each.value.location
  project_id    = var.project_id
  repository_id = each.key
}

module "cloud_build" {
  for_each = var.pipelines

  source = "./cloud_build"

  included      = each.value.cloud_build["included"]
  path          = each.value.cloud_build["path"]
  project_id    = var.project_id
  repo_name     = var.repo_id
  substitutions = local.cloud_build_substitutions[each.key]
  trigger_name  = join("-", [var.environment, each.key])
}
