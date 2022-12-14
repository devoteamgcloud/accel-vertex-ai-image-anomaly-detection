variable "project_id" {
  type        = string
  description = "The project ID of the Cloud Build trigger."
}

variable "trigger_name" {
  type        = string
  description = "The name of the trigger."
}

variable "branch_regex" {
  type        = string
  description = "The regex of the branch to run the trigger."
  default     = ".*"
}

variable "repo_name" {
  type        = string
  description = "The name of the repository."
}

variable "substitutions" {
  type        = map(string)
  description = "The subsitutions to perform in Cloud Build"
}

variable "path" {
  type        = string
  description = "The path to the Cloud Build file."
}

variable "included" {
  type        = list(string)
  description = "The file paths that trigger the trigger."
}
