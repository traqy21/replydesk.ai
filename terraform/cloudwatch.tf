# ─────────────────────────────────────────────
# CloudWatch — Log Group
# ─────────────────────────────────────────────

resource "aws_cloudwatch_log_group" "app" {
  name              = "/replydesk-ai/app"
  retention_in_days = var.log_retention_days

  tags = {
    App = var.app_name
  }
}

# ─────────────────────────────────────────────
# CloudWatch — Metric Alarms
# ─────────────────────────────────────────────

# Alarm when error rate spikes (5+ errors in 5 minutes)
resource "aws_cloudwatch_metric_alarm" "error_rate" {
  alarm_name          = "${var.app_name}-error-rate"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "ErrorCount"
  namespace           = "ReplyDeskAI"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Triggered when 5+ errors occur within 5 minutes"
  treat_missing_data  = "notBreaching"
}

# Alarm for account lockouts (brute-force signal)
resource "aws_cloudwatch_metric_alarm" "lockout_rate" {
  alarm_name          = "${var.app_name}-account-lockouts"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "AccountLockouts"
  namespace           = "ReplyDeskAI"
  period              = 300
  statistic           = "Sum"
  threshold           = 3
  alarm_description   = "Triggered when 3+ accounts are locked out within 5 minutes"
  treat_missing_data  = "notBreaching"
}
