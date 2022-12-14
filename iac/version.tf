terraform {
  required_providers {
    google = {
      version = "~> 4.10.0"
    }
    google-beta = {
      version = "~> 4.10.0"
    }
  }

  backend "gcs" {}
}
