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

variable "api_base_url" {
  type        = string
  description = "API Gateway base URL exposed to the frontend runtime config."
}

variable "websocket_api_url" {
  type        = string
  description = "API Gateway WebSocket URL exposed to the frontend runtime config."
  default     = ""
}

variable "max_file_size_mb" {
  type        = number
  description = "Maximum file size exposed to the frontend runtime config."
  default     = 100
}

variable "tags" {
  type        = map(string)
  description = "Common tags."
  default     = {}
}
