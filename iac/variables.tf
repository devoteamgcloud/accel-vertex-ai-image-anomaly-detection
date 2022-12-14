variable "environment" {
  type        = string
  description = "The environment of this deployment (e.g. dev, uat, prod)"
}

variable "project_id" {
  type        = string
  description = "Project ID of the project"
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "artifact_location" {
  type = string
}

variable "repo_id" {
  type        = string
  description = "The ID of the repository containing pipelines definitions in Google Source Repositories."
}

variable "pipeline_bucket" {
  type        = string
  description = "Bucket used for the pipeline artifacts."
}

variable "model_bucket" {
  type        = string
  description = "Bucket used for the model artifacts."
}

variable "pipeline_service_account_name" {
  type        = string
  description = "Name of the service account for the pipeline."
}

variable "pipeline_service_account_users" {
  type        = list(any)
  description = "Users of the service account for the pipeline."
}

variable "pipelines" {
  type = map(object({
    cloud_build = object({
      included      = list(string)
      path          = string
      substitutions = map(string)
    })
  }))
  description = "Defines the pipelines to be built."
}
