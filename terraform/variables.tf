variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "app_name" {
  description = "Application name used for resource naming"
  type        = string
  default     = "replydesk-ai"
}

variable "openai_api_key" {
  description = "OpenAI API key (stored in Secrets Manager)"
  type        = string
  sensitive   = true
}

variable "cpu" {
  description = "CPU units for App Runner (1024 = 1 vCPU)"
  type        = string
  default     = "256"
}

variable "memory" {
  description = "Memory in MB for App Runner"
  type        = string
  default     = "512"
}

variable "min_instances" {
  description = "Minimum number of instances"
  type        = number
  default     = 1
}

variable "max_instances" {
  description = "Maximum number of instances"
  type        = number
  default     = 2
}

variable "ses_sender_email" {
  description = "Verified SES email address used to send password reset emails"
  type        = string
  default     = "noreply@replydesk.ai"
}

variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
}
