variable "project_name" {
  type        = string
  description = "Project name."
}

variable "environment" {
  type        = string
  description = "Environment name."
}

variable "cluster_arn" {
  type        = string
  description = "ECS cluster ARN."
}

variable "task_definition_arn" {
  type        = string
  description = "Worker task definition ARN."
}

variable "task_execution_role_arn" {
  type        = string
  description = "Worker execution role ARN."
}

variable "task_role_arn" {
  type        = string
  description = "Worker task role ARN."
}

variable "worker_security_group_id" {
  type        = string
  description = "Worker security group ID."
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnets for ECS task."
}

variable "jobs_table_name" {
  type        = string
  description = "DynamoDB jobs table name."
}

variable "jobs_table_arn" {
  type        = string
  description = "DynamoDB jobs table ARN."
}

variable "tags" {
  type        = map(string)
  description = "Common tags."
  default     = {}
}

