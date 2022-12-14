resource "google_storage_bucket" "pipeline" {
  name                        = var.pipeline_bucket
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "model" {
  name                        = var.model_bucket
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true
}
