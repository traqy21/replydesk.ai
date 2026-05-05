# ─────────────────────────────────────────────
# App Runner Service
# ─────────────────────────────────────────────
resource "aws_apprunner_service" "app" {
  service_name = var.app_name

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_ecr.arn
    }

    image_repository {
      image_configuration {
        port = "8501"

        runtime_environment_secrets = {
          OPENAI_API_KEY = aws_secretsmanager_secret.openai_key.arn
        }

        runtime_environment_variables = {
          DYNAMODB_TABLE   = aws_dynamodb_table.users.name
          AWS_REGION       = var.aws_region
          SES_SENDER_EMAIL = var.ses_sender_email
          APP_URL          = "https://${aws_apprunner_service.app.service_url}"
          APP_NAME         = var.app_name
          LOG_LEVEL        = "INFO"
        }
      }

      image_identifier      = "${aws_ecr_repository.app.repository_url}:latest"
      image_repository_type = "ECR"
    }

    auto_deployments_enabled = true
  }

  instance_configuration {
    cpu               = var.cpu
    memory            = var.memory
    instance_role_arn = aws_iam_role.apprunner_instance.arn
  }

  health_check_configuration {
    protocol            = "HTTP"
    path                = "/_stcore/health"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }

  auto_scaling_configuration_arn = aws_apprunner_auto_scaling_configuration_version.app.arn

  tags = {
    App = var.app_name
  }
}

# ─────────────────────────────────────────────
# Auto Scaling Configuration
# ─────────────────────────────────────────────
resource "aws_apprunner_auto_scaling_configuration_version" "app" {
  auto_scaling_configuration_name = "${var.app_name}-scaling"

  max_concurrency = 50
  max_size        = var.max_instances
  min_size        = var.min_instances

  tags = {
    App = var.app_name
  }
}
