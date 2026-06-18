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

variable "api_name" {
  type        = string
  description = "API Gateway name."
  default     = ""
}

variable "api_log_group_name" {
  type        = string
  description = "API log group name."
}

variable "worker_log_group_name" {
  type        = string
  description = "Worker log group name."
}

variable "state_machine_arn" {
  type        = string
  description = "State machine ARN."
}

variable "state_machine_name" {
  type        = string
  description = "State machine name."
}

variable "jobs_table_name" {
  type        = string
  description = "Jobs table name."
}

variable "failed_jobs_alarm_threshold" {
  type        = number
  description = "Failed worker log events threshold."
  default     = 5
}

variable "tags" {
  type        = map(string)
  description = "Common tags."
  default     = {}
}
