variable "project_name" {
  type        = string
  description = "Project name used for state resources."
  default     = "morphix"
}

variable "environment" {
  type        = string
  description = "Environment name."
  default     = "dev"
}

variable "state_bucket_name" {
  type        = string
  description = "Remote state bucket name."
}

variable "lock_table_name" {
  type        = string
  description = "DynamoDB table used by Terraform state locking."
}

variable "tags" {
  type        = map(string)
  description = "Common tags."
  default     = {}
}

