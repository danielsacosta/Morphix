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

variable "cluster_arn" {
  type        = string
  description = "ECS cluster ARN."
}

variable "vpc_id" {
  type        = string
  description = "VPC ID for worker security group."
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs where worker runs."
}

variable "worker_image_uri" {
  type        = string
  description = "Worker image URI. If empty, repository latest is used."
  default     = ""
}

variable "repository_force_delete" {
  type        = bool
  description = "Allow ECR repository deletion with images during destroy."
  default     = false
}

variable "worker_cpu" {
  type        = number
  description = "Fargate task CPU."
  default     = 1024
}

variable "worker_memory" {
  type        = number
  description = "Fargate task memory."
  default     = 2048
}

variable "worker_ephemeral_storage_gib" {
  type        = number
  description = "Worker ephemeral storage in GiB."
  default     = 30
}

variable "input_bucket_arn" {
  type        = string
  description = "Input bucket ARN."
}

variable "output_bucket_arn" {
  type        = string
  description = "Output bucket ARN."
}

variable "jobs_table_arn" {
  type        = string
  description = "Jobs table ARN."
}

variable "jobs_table_name" {
  type        = string
  description = "Jobs table name."
}

variable "input_bucket_name" {
  type        = string
  description = "Input bucket name."
}

variable "output_bucket_name" {
  type        = string
  description = "Output bucket name."
}

variable "conversion_timeout_seconds" {
  type        = number
  description = "Maximum conversion time in seconds."
  default     = 900
}

variable "tags" {
  type        = map(string)
  description = "Common tags."
  default     = {}
}
