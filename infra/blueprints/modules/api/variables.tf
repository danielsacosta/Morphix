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

variable "cluster_arn" {
  type        = string
  description = "ECS cluster ARN used by the conversion state machine."
}

variable "task_definition_arn" {
  type        = string
  description = "Worker task definition ARN used by the conversion state machine."
}

variable "task_execution_role_arn" {
  type        = string
  description = "Worker execution role ARN passed by Step Functions."
}

variable "task_role_arn" {
  type        = string
  description = "Worker task role ARN passed by Step Functions."
}

variable "worker_security_group_id" {
  type        = string
  description = "Worker security group used by the conversion state machine."
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs used by the conversion state machine."
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
