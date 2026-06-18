variable "project_name" {
  type        = string
  description = "Project name."
}

variable "environment" {
  type        = string
  description = "Environment name."
}

variable "github_repository" {
  type        = string
  description = "GitHub repository in owner/name format."
}

variable "tags" {
  type        = map(string)
  description = "Common tags."
  default     = {}
}

