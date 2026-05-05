"""Feedback storage — supports JSON file (local) and DynamoDB (production).

Mirrors the same dual-backend pattern used for user storage in auth.py.
"""

import json
import os
from datetime import datetime
from logger import get_logger

log = get_logger("feedback")

FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), "feedback.json")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# DynamoDB uses a separate table for feedback
FEEDBACK_TABLE_NAME = f"{os.getenv('APP_NAME', 'replydesk-ai')}-feedback"


# ─────────────────────────────────────────────
# Backend detection
# ─────────────────────────────────────────────

def _use_dynamodb() -> bool:
    """Use DynamoDB when the DYNAMODB_TABLE env var is set (production)."""
    return bool(DYNAMODB_TABLE)


def _get_feedback_table():
    """Get the DynamoDB feedback table resource."""
    import boto3
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    return dynamodb.Table(FEEDBACK_TABLE_NAME)


# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────

def save_feedback(entry: dict):
    """Persist a single feedback entry."""
    # Ensure a unique ID for DynamoDB primary key
    if "id" not in entry:
        import uuid
        entry["id"] = str(uuid.uuid4())

    try:
        if _use_dynamodb():
            table = _get_feedback_table()
            table.put_item(Item=entry)
        else:
            entries = load_all_feedback()
            entries.append(entry)
            with open(FEEDBACK_FILE, "w") as f:
                json.dump(entries, f, indent=2)
        log.info("feedback_saved", extra={"email": entry.get("email"), "category": entry.get("category")})
    except Exception as e:
        log.error("feedback_save_failed", extra={"error": str(e)}, exc_info=True)
        raise


def load_all_feedback() -> list:
    """Load all feedback entries."""
    if _use_dynamodb():
        table = _get_feedback_table()
        response = table.scan()
        items = response.get("Items", [])
        # Handle DynamoDB pagination
        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            items.extend(response.get("Items", []))
        return sorted(items, key=lambda x: x.get("timestamp", ""))
    else:
        if not os.path.exists(FEEDBACK_FILE):
            return []
        with open(FEEDBACK_FILE, "r") as f:
            return json.load(f)


def load_user_feedback(email: str) -> list:
    """Load feedback entries for a specific user."""
    all_entries = load_all_feedback()
    return [e for e in all_entries if e.get("email") == email]
