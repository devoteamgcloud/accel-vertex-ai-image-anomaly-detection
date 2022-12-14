resource "google_cloudbuild_trigger" "default" {
  project        = var.project_id
  name           = var.trigger_name
  substitutions  = var.substitutions
  filename       = var.path
  included_files = var.included

  trigger_template {
    branch_name = var.branch_regex
    repo_name   = var.repo_name
  }
}
