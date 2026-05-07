"""Email service — abstraction layer supporting Resend (primary) and AWS SES (fallback).

To switch providers, change EMAIL_PROVIDER env var:
  - "resend" (default) — uses Resend API
  - "ses"              — uses AWS SES

Required env vars:
  - RESEND_API_KEY     — Resend API key (when using Resend)
  - SES_SENDER_EMAIL   — From address (both providers)
  - AWS_REGION         — AWS region (when using SES)
"""

import os
from logger import get_logger

log = get_logger("email")

EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "resend")
SES_SENDER_EMAIL = os.getenv("SES_SENDER_EMAIL", "noreply@replydesk-ai.com")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")


def send_email(to: str, subject: str, html: str, text: str) -> tuple[bool, str]:
    """Send an email using the configured provider.
    Returns (success, message).
    """
    if EMAIL_PROVIDER == "ses":
        return _send_via_ses(to, subject, html, text)
    return _send_via_resend(to, subject, html, text)


def _send_via_resend(to: str, subject: str, html: str, text: str) -> tuple[bool, str]:
    """Send email via Resend."""
    if not RESEND_API_KEY:
        log.error("resend_missing_key", extra={"to": to})
        return False, "RESEND_API_KEY is not configured."

    try:
        import resend
        resend.api_key = RESEND_API_KEY

        resend.Emails.send({
            "from": SES_SENDER_EMAIL,
            "to": [to],
            "subject": subject,
            "html": html,
            "text": text,
        })

        log.info("email_sent", extra={"provider": "resend", "to": to, "subject": subject})
        return True, "Email sent."
    except Exception as e:
        log.error("resend_send_failed", extra={"to": to, "error": str(e)}, exc_info=True)
        return False, f"Failed to send email: {e}"


def _send_via_ses(to: str, subject: str, html: str, text: str) -> tuple[bool, str]:
    """Send email via AWS SES."""
    try:
        import boto3
        ses = boto3.client("ses", region_name=AWS_REGION)
        ses.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={"ToAddresses": [to]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": text, "Charset": "UTF-8"},
                    "Html": {"Data": html, "Charset": "UTF-8"},
                },
            },
        )
        log.info("email_sent", extra={"provider": "ses", "to": to, "subject": subject})
        return True, "Email sent."
    except Exception as e:
        log.error("ses_send_failed", extra={"to": to, "error": str(e)}, exc_info=True)
        return False, f"Failed to send email: {e}"
