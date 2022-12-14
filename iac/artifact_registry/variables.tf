variable "project_id" {
  type        = string
  description = "The project ID of the artifact registry."
}

variable "repository_id" {
  type        = string
  description = "The name of the artifact registry repository."
}

variable "location" {
  type        = string
  description = "The location of the artifact registry repository."
}

variable "description" {
  type        = string
  description = "A description of the artifact repository."
}

variable "format" {
  type        = string
  description = "The format of the artifacts in this repository."
}
