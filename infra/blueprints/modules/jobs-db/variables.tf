variable "project_name" {
  type        = string
  description = "Project name."
}

variable "environment" {
  type        = string
  description = "Environment name."
}

variable "billing_mode" {
  type        = string
  description = "DynamoDB billing mode."
  default     = "PAY_PER_REQUEST"
}

variable "ttl_attribute" {
  type        = string
  description = "TTL attribute name."
  default     = "expires_at"
}

variable "tags" {
  type        = map(string)
  description = "Common tags."
  default     = {}
}

