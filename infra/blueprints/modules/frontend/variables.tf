variable "project_name" {
  type        = string
  description = "Project name."
}

variable "environment" {
  type        = string
  description = "Environment name."
}

variable "frontend_bucket_name" {
  type        = string
  description = "Optional frontend bucket name."
  default     = ""
}

variable "frontend_force_destroy" {
  type        = bool
  description = "Allow bucket deletion with objects."
  default     = false
}

variable "frontend_price_class" {
  type        = string
  description = "CloudFront price class."
  default     = "PriceClass_100"
}

variable "tags" {
  type        = map(string)
  description = "Common tags."
  default     = {}
}

