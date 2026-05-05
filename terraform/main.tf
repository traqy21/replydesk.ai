terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state — prevents corruption from concurrent applies
  # Uncomment and configure before first production deploy:
  # backend "s3" {
  #   bucket         = "replydesk-terraform-state"
  #   key            = "prod/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region
}

# ─────────────────────────────────────────────
# ECR Repository
# ─────────────────────────────────────────────
resource "aws_ecr_repository" "app" {
  name                 = var.app_name
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}

# ─────────────────────────────────────────────
# Secrets Manager — OpenAI API Key
# ─────────────────────────────────────────────
resource "aws_secretsmanager_secret" "openai_key" {
  name        = "${var.app_name}/openai-api-key"
  description = "OpenAI API key for Replydesk AI"
}

resource "aws_secretsmanager_secret_version" "openai_key" {
  secret_id     = aws_secretsmanager_secret.openai_key.id
  secret_string = var.openai_api_key
}

# ─────────────────────────────────────────────
# Secrets Manager — Admin Credentials
# ─────────────────────────────────────────────
resource "aws_secretsmanager_secret" "admin_email" {
  name        = "${var.app_name}/admin-email"
  description = "Admin email for Replydesk AI"
}

resource "aws_secretsmanager_secret_version" "admin_email" {
  secret_id     = aws_secretsmanager_secret.admin_email.id
  secret_string = var.admin_email
}

resource "aws_secretsmanager_secret" "admin_password" {
  name        = "${var.app_name}/admin-password"
  description = "Admin password for Replydesk AI"
}

resource "aws_secretsmanager_secret_version" "admin_password" {
  secret_id     = aws_secretsmanager_secret.admin_password.id
  secret_string = var.admin_password
}

# ─────────────────────────────────────────────
# DynamoDB — User Storage
# ─────────────────────────────────────────────
resource "aws_dynamodb_table" "users" {
  name         = "${var.app_name}-users"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "email"

  attribute {
    name = "email"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    App = var.app_name
  }
}

# ─────────────────────────────────────────────
# DynamoDB — Feedback Storage
# ─────────────────────────────────────────────
resource "aws_dynamodb_table" "feedback" {
  name         = "${var.app_name}-feedback"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    App = var.app_name
  }
}

# ─────────────────────────────────────────────
# IAM Role for ECR Access (GitHub Actions / CI)
# ─────────────────────────────────────────────
resource "aws_iam_role" "ecr_push" {
  name = "${var.app_name}-ecr-push-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "build.apprunner.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecr_push" {
  role       = aws_iam_role.ecr_push.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}
