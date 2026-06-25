variable "project_name" {
  type        = string
  description = "Project name."
}

variable "environment" {
  type        = string
  description = "Environment name."
}

variable "aws_region" {
  type        = string
  description = "AWS region."
  default     = "us-east-1"
}

variable "api_package_path" {
  type        = string
  description = "Local path to the Lambda zip package. If empty, the API runtime is not created."
  default     = ""
}

variable "state_machine_definition_path" {
  type        = string
  description = "Local path to the API-owned Step Functions ASL JSON definition."
}

variable "jobs_table_name" {
  type        = string
  description = "Jobs table name."
}

variable "jobs_table_arn" {
  type        = string
  description = "Jobs table ARN."
}

variable "jobs_table_stream_arn" {
  type        = string
  description = "Jobs table DynamoDB Stream ARN."
  default     = ""
}

variable "input_bucket_name" {
  type        = string
  description = "Input bucket name."
}

variable "input_bucket_arn" {
  type        = string
  description = "Input bucket ARN."
}

variable "output_bucket_name" {
  type        = string
  description = "Output bucket name."
}

variable "output_bucket_arn" {
  type        = string
  description = "Output bucket ARN."
}

variable "conversion_queue_url" {
  type        = string
  description = "SQS conversion queue URL."
}

variable "conversion_queue_arn" {
  type        = string
  description = "SQS conversion queue ARN."
}

variable "worker_callback_timeout_seconds" {
  type        = number
  description = "Maximum time Step Functions waits for a worker callback."
  default     = 1200
}

variable "websocket_connection_ttl_seconds" {
  type        = number
  description = "Seconds to keep idle websocket connection records."
  default     = 86400
}

variable "max_file_size_mb" {
  type        = number
  description = "Maximum file size accepted by API."
  default     = 100
}

variable "allowed_origins" {
  type        = list(string)
  description = "CORS allowed origins."
  default     = ["http://localhost:5173"]
}

variable "tags" {
  type        = map(string)
  description = "Common tags."
  default     = {}
}
