output "app_url" {
  description = "URL of the deployed Replydesk AI application"
  value       = "https://${aws_apprunner_service.app.service_url}"
}

output "ecr_repository_url" {
  description = "ECR repository URL for pushing Docker images"
  value       = aws_ecr_repository.app.repository_url
}

output "dynamodb_table_name" {
  description = "DynamoDB table name for user storage"
  value       = aws_dynamodb_table.users.name
}

output "service_arn" {
  description = "ARN of the App Runner service"
  value       = aws_apprunner_service.app.arn
}
