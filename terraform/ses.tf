# ─────────────────────────────────────────────
# SES — Email Identity for Password Reset
# ─────────────────────────────────────────────

resource "aws_ses_email_identity" "sender" {
  email = var.ses_sender_email
}

# ─────────────────────────────────────────────
# IAM — Allow App Runner to send via SES
# ─────────────────────────────────────────────

resource "aws_iam_role_policy" "apprunner_ses" {
  name = "${var.app_name}-apprunner-ses-policy"
  role = aws_iam_role.apprunner_instance.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "ses:FromAddress" = var.ses_sender_email
          }
        }
      }
    ]
  })
}
