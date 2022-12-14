variable "project_id" {
  type        = string
  description = "Project ID. Must be globally unique in GCP"
}

variable "region" {
  description = "GCP region"
  type        = string
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
