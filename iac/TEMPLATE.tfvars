environment                   = "dev"
project_id                    = "<PROJECT_ID>"
region                        = "<REGION>"
artifact_location             = "<REGION>"
repo_id                       = "<CLOUD_SOURCE_REPO_ID>"
pipeline_bucket               = "<PIPELINE_BUCKET_NAME>"
model_bucket                  = "<MODEL_BUCKET_NAME>"
pipeline_service_account_name = "sa-vertex-pipeline"
pipeline_service_account_users = [
  "<USER_EMAIL>",
]
pipelines = {
  "pipeline" = {
    "cloud_build" = {
      included      = ["**"]
      substitutions = {}
      path          = "cloudbuild.yaml"
    }
  }
}
