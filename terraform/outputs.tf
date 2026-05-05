output "app_url" {
  description = "Public URL of the application (point your domain A record to the elastic_ip)"
  value       = "https://${var.domain}"
}

output "elastic_ip" {
  description = "Elastic IP address — point your domain A record here"
  value       = aws_eip.app.public_ip
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

output "cloudwatch_log_group" {
  description = "CloudWatch log group for application logs"
  value       = aws_cloudwatch_log_group.app.name
}

output "github_actions_role_arn" {
  description = "IAM role ARN to set as AWS_DEPLOY_ROLE_ARN in GitHub Actions secrets"
  value       = aws_iam_role.github_actions_deploy.arn
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ~/.ssh/your-key ec2-user@${aws_eip.app.public_ip}"
}
