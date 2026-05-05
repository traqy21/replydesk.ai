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

variable "instance_type" {
  description = "EC2 instance type. t4g.micro (~$6/mo) is the recommended minimum. t4g.nano (~$3/mo) may run out of memory under load."
  type        = string
  default     = "t4g.micro"
}

variable "ssh_public_key" {
  description = "SSH public key for EC2 access (contents of your ~/.ssh/id_rsa.pub or similar)"
  type        = string
}

variable "ssh_allowed_cidr" {
  description = "CIDR block allowed to SSH into the instance. Restrict to your IP for security (e.g. 1.2.3.4/32)"
  type        = string
  default     = "0.0.0.0/0"
}

variable "domain" {
  description = "Your domain name (e.g. app.replydesk.ai). Point an A record to the Elastic IP after deploy. Used for SSL via Let's Encrypt."
  type        = string
  default     = "localhost"
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

variable "admin_email" {
  description = "Default admin account email"
  type        = string
  sensitive   = true
}

variable "admin_password" {
  description = "Default admin account password"
  type        = string
  sensitive   = true
}

variable "github_repo" {
  description = "GitHub repository in org/repo format (e.g. myorg/replydesk-ai) — used to scope OIDC trust"
  type        = string
}

variable "app_url" {
  description = "Public app URL — set to your domain after first deploy (used in password reset emails)"
  type        = string
  default     = "https://localhost"
}
