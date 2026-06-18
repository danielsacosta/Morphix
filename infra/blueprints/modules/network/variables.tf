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

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR."
  default     = "10.30.0.0/16"
}

variable "public_subnet_cidrs" {
  type        = list(string)
  description = "Public subnet CIDRs."
  default     = ["10.30.0.0/24", "10.30.1.0/24"]
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "Private subnet CIDRs."
  default     = ["10.30.10.0/24", "10.30.11.0/24"]
}

variable "enable_nat_gateway" {
  type        = bool
  description = "Enable one NAT gateway for private subnets."
  default     = true
}

variable "enable_s3_endpoint" {
  type        = bool
  description = "Enable S3 gateway endpoint."
  default     = true
}

variable "enable_dynamodb_endpoint" {
  type        = bool
  description = "Enable DynamoDB gateway endpoint."
  default     = true
}

variable "enable_ecr_endpoints" {
  type        = bool
  description = "Enable ECR interface endpoints."
  default     = false
}

variable "enable_cloudwatch_logs_endpoint" {
  type        = bool
  description = "Enable CloudWatch Logs interface endpoint."
  default     = false
}

variable "tags" {
  type        = map(string)
  description = "Common tags."
  default     = {}
}
