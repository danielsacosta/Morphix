variable "project_name" {
  type        = string
  description = "Project name."
}

variable "environment" {
  type        = string
  description = "Environment name."
}

variable "visibility_timeout_seconds" {
  type        = number
  description = "SQS visibility timeout. Must be greater than the worker conversion timeout."
  default     = 1200
}

variable "message_retention_seconds" {
  type        = number
  description = "Main queue message retention."
  default     = 1209600
}

variable "dlq_message_retention_seconds" {
  type        = number
  description = "Dead-letter queue message retention."
  default     = 1209600
}

variable "receive_wait_time_seconds" {
  type        = number
  description = "Long-poll receive wait time."
  default     = 20
}

variable "max_receive_count" {
  type        = number
  description = "Failed receives before moving a message to the DLQ."
  default     = 3
}

variable "tags" {
  type        = map(string)
  description = "Common tags."
  default     = {}
}
