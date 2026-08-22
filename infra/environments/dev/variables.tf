variable "aws_region" {
  description = "AWS region for the isolated environment."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment identifier used in names and access policies."
  type        = string
  default     = "dev"
}

variable "redis_auth_token" {
  description = "Redis AUTH token injected from an external secret store."
  type        = string
  sensitive   = true
}
