"""Centralised logging for Replydesk AI.

- Local / dev  : logs to stdout at DEBUG level (plain text)
- Production   : logs to stdout AND CloudWatch Logs via watchtower (JSON)

Usage:
    from logger import get_logger
    log = get_logger(__name__)

    log.info("user_login", extra={"email": email})
    log.warning("rate_limit_hit", extra={"email": email})
    log.error("openai_error", extra={"error": str(e), "tool": tool})
"""

import logging
import os
import json
from datetime import datetime, timezone

APP_NAME = os.getenv("APP_NAME", "replydesk-ai")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
LOG_GROUP = f"/replydesk-ai/app"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# ─────────────────────────────────────────────
# JSON formatter — structured logs for CloudWatch Insights
# ─────────────────────────────────────────────

class JsonFormatter(logging.Formatter):
    """Emit each log record as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Merge any extra fields passed via extra={...}
        skip = {
            "name", "msg", "args", "levelname", "levelno", "pathname",
            "filename", "module", "exc_info", "exc_text", "stack_info",
            "lineno", "funcName", "created", "msecs", "relativeCreated",
            "thread", "threadName", "processName", "process", "message",
            "taskName",
        }
        for key, value in record.__dict__.items():
            if key not in skip:
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


# ─────────────────────────────────────────────
# Logger factory
# ─────────────────────────────────────────────

def _build_root_logger():
    """Configure the root logger once at import time."""
    root = logging.getLogger("replydesk")
    if root.handlers:
        # Already configured (Streamlit reruns this module on every interaction)
        return root

    root.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # ── stdout handler (always on) ──────────────────────────────────────
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(JsonFormatter())
    root.addHandler(stream_handler)

    # ── CloudWatch handler (production only) ────────────────────────────
    if os.getenv("DYNAMODB_TABLE"):  # production signal
        try:
            import watchtower
            import boto3

            cw_client = boto3.client("logs", region_name=AWS_REGION)
            cw_handler = watchtower.CloudWatchLogHandler(
                log_group_name=LOG_GROUP,
                log_stream_name=APP_NAME,
                boto3_client=cw_client,
                send_interval=5,        # flush every 5 seconds
                max_batch_size=10_000,  # bytes
                max_batch_count=100,
            )
            cw_handler.setFormatter(JsonFormatter())
            root.addHandler(cw_handler)
            root.info(
                "cloudwatch_logging_enabled",
                extra={"log_group": LOG_GROUP, "region": AWS_REGION},
            )
        except Exception as e:
            root.warning(f"CloudWatch logging unavailable: {e}")

    return root


_root_logger = _build_root_logger()


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the replydesk namespace."""
    return logging.getLogger(f"replydesk.{name}")
