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

output "dynamodb_feedback_table_name" {
  description = "DynamoDB table name for feedback storage"
  value       = aws_dynamodb_table.feedback.name
}

output "ses_sender_email" {
  description = "SES verified sender email for password reset"
  value       = aws_ses_email_identity.sender.email
}


output "service_arn" {
  description = "ARN of the App Runner service"
  value       = aws_apprunner_service.app.arn
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for application logs"
  value       = aws_cloudwatch_log_group.app.name
}
