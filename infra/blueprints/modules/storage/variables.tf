variable "project_name" {
  type        = string
  description = "Project name."
}

variable "environment" {
  type        = string
  description = "Environment name."
}

variable "input_bucket_name" {
  type        = string
  description = "Optional input bucket name."
  default     = ""
}

variable "output_bucket_name" {
  type        = string
  description = "Optional output bucket name."
  default     = ""
}

variable "input_retention_days" {
  type        = number
  description = "Input file retention days."
  default     = 1
}

variable "output_retention_days" {
  type        = number
  description = "Output file retention days."
  default     = 7
}

variable "max_upload_size_mb" {
  type        = number
  description = "Documented max upload size for clients."
  default     = 100
}

variable "allowed_origins" {
  type        = list(string)
  description = "Allowed CORS origins for browser uploads."
  default     = ["http://localhost:5173"]
}

variable "force_destroy" {
  type        = bool
  description = "Allow deletion with objects."
  default     = false
}

variable "tags" {
  type        = map(string)
  description = "Common tags."
  default     = {}
}

