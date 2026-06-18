variable "project_name" {
  type        = string
  description = "Project name."
}

variable "environment" {
  type        = string
  description = "Environment name."
}

variable "enable_container_insights" {
  type        = bool
  description = "Enable ECS Container Insights."
  default     = true
}

variable "tags" {
  type        = map(string)
  description = "Common tags."
  default     = {}
}

