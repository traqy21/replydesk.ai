"""Authentication module — supports JSON file (local) and DynamoDB (production).

Features:
- Bcrypt password hashing
- Session timeout (auto-logout after inactivity)
- Rate limiting on generations
- Brute-force protection with account lockout
"""

import streamlit as st
import json
import os
import re
import secrets
from datetime import datetime, timedelta

import bcrypt
from logger import get_logger

log = get_logger("auth")

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Session timeout in minutes
SESSION_TIMEOUT_MINUTES = 30

# Rate limiting: max generations per day per user
MAX_GENERATIONS_PER_DAY = 10

# Brute-force protection
MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

# Password reset token expiry in minutes
RESET_TOKEN_EXPIRY_MINUTES = 30

# SES config
SES_SENDER_EMAIL = os.getenv("SES_SENDER_EMAIL", "noreply@replydesk-ai.com")
APP_URL = os.getenv("APP_URL", "http://localhost:8501")

# Job positions dropdown options
JOB_POSITIONS = [
    "Virtual Assistant",
    "Executive Assistant",
    "Administrative Assistant",
    "Customer Support Specialist",
    "Social Media Manager",
    "Content Writer",
    "Copywriter",
    "Project Manager",
    "Operations Manager",
    "Marketing Specialist",
    "Sales Representative",
    "Account Manager",
    "Human Resources",
    "Bookkeeper / Accountant",
    "Data Entry Specialist",
    "Graphic Designer",
    "Web Developer",
    "Software Engineer",
    "IT Support",
    "Team Lead / Supervisor",
    "Freelancer",
    "Business Owner",
    "Student / Intern",
    "Other",
]


# ─────────────────────────────────────────────
# Storage Backend
# ─────────────────────────────────────────────

def _use_dynamodb() -> bool:
    """Check if DynamoDB should be used (production mode)."""
    return bool(DYNAMODB_TABLE)


def _get_dynamodb_table():
    """Get the DynamoDB table resource."""
    import boto3
    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    return dynamodb.Table(DYNAMODB_TABLE)


def _load_user_dynamo(email: str) -> dict | None:
    """Load a single user from DynamoDB."""
    table = _get_dynamodb_table()
    response = table.get_item(Key={"email": email.lower()})
    return response.get("Item")


def _save_user_dynamo(user_data: dict):
    """Save a user to DynamoDB."""
    table = _get_dynamodb_table()
    table.put_item(Item=user_data)


def _user_exists_dynamo(email: str) -> bool:
    """Check if a user exists in DynamoDB."""
    return _load_user_dynamo(email) is not None


# ─────────────────────────────────────────────
# JSON File Storage (local development)
# ─────────────────────────────────────────────

def _load_users_json() -> dict:
    """Load users from the JSON file."""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def _save_users_json(users: dict):
    """Save users to the JSON file."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


# ─────────────────────────────────────────────
# Password Hashing (bcrypt)
# ─────────────────────────────────────────────

def _hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash. Also supports legacy SHA-256."""
    # Support legacy SHA-256 hashes (64 hex chars) for backward compatibility
    if len(hashed) == 64 and all(c in "0123456789abcdef" for c in hashed):
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    # Bcrypt verification
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except (ValueError, TypeError):
        return False


def _is_valid_email(email: str) -> bool:
    """Check if the email format is valid."""
    return bool(email and re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


# ─────────────────────────────────────────────
# Session Timeout
# ─────────────────────────────────────────────

def _update_last_activity():
    """Update the last activity timestamp."""
    st.session_state.last_activity = datetime.now()


def _check_session_timeout() -> bool:
    """Check if the session has timed out. Returns True if expired."""
    if "last_activity" not in st.session_state:
        return False

    elapsed = datetime.now() - st.session_state.last_activity
    return elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES)


# ─────────────────────────────────────────────
# Rate Limiting — persisted to user record
# ─────────────────────────────────────────────

def _load_generation_count(email: str) -> tuple[int, str]:
    """Load today's generation count from the user record.
    Returns (count, date).
    """
    today = datetime.now().strftime("%Y-%m-%d")
    user = _get_user_profile(email)
    stored_date = user.get("rate_limit_date", "")

    # If total_generations doesn't exist yet, seed it from generation_count
    if "total_generations" not in user:
        seed_total = int(user.get("generation_count", 0)) if stored_date == today else 0
        st.session_state.total_generations = seed_total
        # Persist the seeded value
        _save_generation_count(email,
                               int(user.get("generation_count", 0)),
                               stored_date or today,
                               seed_total)
    else:
        st.session_state.total_generations = int(user.get("total_generations", 0))

    if stored_date != today:
        return 0, today
    return int(user.get("generation_count", 0)), today


def _save_generation_count(email: str, count: int, date: str, total: int = None):
    """Persist the generation count to the user record."""
    if _use_dynamodb():
        update_expr = "SET generation_count = :c, rate_limit_date = :d"
        expr_values = {":c": count, ":d": date}
        if total is not None:
            update_expr += ", total_generations = :t"
            expr_values[":t"] = total
        _get_dynamodb_table().update_item(
            Key={"email": email.lower()},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values,
        )
    else:
        users = _load_users_json()
        if email.lower() in users:
            users[email.lower()]["generation_count"] = count
            users[email.lower()]["rate_limit_date"] = date
            if total is not None:
                users[email.lower()]["total_generations"] = total
            _save_users_json(users)


def check_rate_limit() -> tuple[bool, str]:
    """Check if the user has exceeded the daily generation limit.
    Loads count from storage and syncs to session state.
    Returns (allowed, message).
    """
    email = st.session_state.get("email", "")
    today = datetime.now().strftime("%Y-%m-%d")

    # Load from storage if session is stale or new day
    if (st.session_state.get("rate_limit_date") != today or
            not st.session_state.get("_count_loaded")):
        if email:
            count, date = _load_generation_count(email)
            st.session_state.generation_count = count
            st.session_state.rate_limit_date = date
            st.session_state._count_loaded = True
        else:
            if st.session_state.get("rate_limit_date") != today:
                st.session_state.rate_limit_date = today
                st.session_state.generation_count = 0

    if st.session_state.generation_count >= MAX_GENERATIONS_PER_DAY:
        return False, (
            f"You've reached your daily limit of {MAX_GENERATIONS_PER_DAY} generations. "
            f"Try again tomorrow."
        )

    return True, ""


def increment_generation_count():
    """Increment the daily generation counter and persist to storage."""
    today = datetime.now().strftime("%Y-%m-%d")
    new_count = st.session_state.get("generation_count", 0) + 1
    new_total = st.session_state.get("total_generations", 0) + 1
    st.session_state.generation_count = new_count
    st.session_state.total_generations = new_total
    st.session_state.rate_limit_date = today

    email = st.session_state.get("email", "")
    if email:
        _save_generation_count(email, new_count, today, new_total)


def get_remaining_generations() -> int:
    """Get the number of remaining generations for today."""
    return max(0, MAX_GENERATIONS_PER_DAY - st.session_state.get("generation_count", 0))


# ─────────────────────────────────────────────
# Auth Logic
# ─────────────────────────────────────────────

def init_auth_state():
    """Initialize authentication session state."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "job_position" not in st.session_state:
        st.session_state.job_position = "Virtual Assistant"
    if "email" not in st.session_state:
        st.session_state.email = ""
    if "auth_page" not in st.session_state:
        st.session_state.auth_page = "login"
    if "generation_count" not in st.session_state:
        st.session_state.generation_count = 0
    if "rate_limit_date" not in st.session_state:
        st.session_state.rate_limit_date = datetime.now().strftime("%Y-%m-%d")


def register_user(email: str, job_position: str, password: str, confirm_password: str) -> tuple[bool, str]:
    """Register a new user. Returns (success, message)."""
    if not _is_valid_email(email):
        return False, "Please enter a valid email address."

    if not job_position:
        return False, "Please select a job position."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    if password != confirm_password:
        return False, "Passwords do not match."

    verification_token = secrets.token_urlsafe(32)

    user_data = {
        "email": email.lower(),
        "job_position": job_position,
        "password_hash": _hash_password(password),
        "is_verified": False,
        "verification_token": verification_token,
    }

    if _use_dynamodb():
        if _user_exists_dynamo(email):
            return False, "This email is already registered."
        _save_user_dynamo(user_data)
    else:
        users = _load_users_json()
        if email.lower() in users:
            return False, "This email is already registered."
        users[email.lower()] = user_data
        _save_users_json(users)

    log.info("user_registered", extra={"email": email.lower(), "job_position": job_position})

    # In production, send verification email
    # In local dev (no DYNAMODB_TABLE), auto-verify so testing works without SES
    if _use_dynamodb():
        _send_verification_email(email.lower(), verification_token)
        return True, "Registration successful! Please check your email to verify your account."
    else:
        # Auto-verify locally
        users = _load_users_json()
        users[email.lower()]["is_verified"] = True
        users[email.lower()].pop("verification_token", None)
        _save_users_json(users)
        return True, "Registration successful! You can now log in."


def _send_verification_email(email: str, token: str):
    """Send an account verification email via AWS SES."""
    verify_url = f"{APP_URL}?verify_token={token}"

    subject = "Verify your Replydesk AI account"
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #1a1a2e;">Verify your email address</h2>
        <p>Thanks for signing up for Replydesk AI! Click the button below to verify your email address and activate your account.</p>
        <a href="{verify_url}"
           style="display:inline-block; padding: 12px 24px; background-color: #4F8EF7;
                  color: #ffffff; text-decoration: none; border-radius: 6px; margin: 16px 0;">
            Verify Email Address
        </a>
        <p style="color: #666; font-size: 13px;">
            If you didn't create an account, you can safely ignore this email.
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;" />
        <p style="color: #999; font-size: 12px;">Replydesk AI — Your AI-powered assistant for professional communication</p>
    </body>
    </html>
    """
    body_text = (
        f"Verify your Replydesk AI account\n\n"
        f"Click the link below to verify your email and activate your account:\n\n"
        f"{verify_url}\n\n"
        f"If you didn't create an account, ignore this email."
    )

    try:
        import boto3
        ses = boto3.client("ses", region_name=AWS_REGION)
        ses.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": body_text, "Charset": "UTF-8"},
                    "Html": {"Data": body_html, "Charset": "UTF-8"},
                },
            },
        )
        log.info("verification_email_sent", extra={"email": email})
    except Exception as e:
        log.error("verification_email_failed", extra={"email": email, "error": str(e)}, exc_info=True)


def verify_email_token(token: str) -> tuple[bool, str]:
    """Verify an email using the token from the verification link.
    Returns (success, message).
    """
    if _use_dynamodb():
        table = _get_dynamodb_table()
        response = table.scan(
            FilterExpression="verification_token = :t",
            ExpressionAttributeValues={":t": token},
        )
        items = response.get("Items", [])
        user = items[0] if items else None
    else:
        users = _load_users_json()
        user = next(
            (u for u in users.values() if u.get("verification_token") == token),
            None,
        )

    if not user:
        return False, "Invalid or expired verification link."

    if user.get("is_verified"):
        return True, "Your email is already verified. You can log in."

    user["is_verified"] = True
    user.pop("verification_token", None)
    _persist_user(user)

    log.info("email_verified", extra={"email": user["email"]})

    # Send welcome email after successful verification
    _send_welcome_email(user["email"])

    return True, "Email verified successfully! You can now log in."


def _send_welcome_email(email: str):
    """Send a welcome email after account verification."""
    subject = "Welcome to Replydesk AI 🎉"
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #1a1a2e;">Welcome to Replydesk AI!</h2>
        <p>Your account is now verified and ready to use. Here's what you can do:</p>
        <ul style="line-height: 2;">
            <li>💬 <strong>Client Reply</strong> — respond to clients professionally</li>
            <li>📧 <strong>Email Generator</strong> — draft emails from rough notes</li>
            <li>📋 <strong>Task Summary</strong> — turn notes into bullet points</li>
            <li>📊 <strong>Daily Report</strong> — generate end-of-day status reports</li>
            <li>🗒️ <strong>Meeting Notes</strong> — structure raw meeting notes</li>
            <li>↩️ <strong>Follow-up Email</strong> — write professional follow-ups</li>
            <li>✏️ <strong>Tone Rewriter</strong> — rewrite any message in a different tone</li>
        </ul>
        <p>You have <strong>10 free generations per day</strong> to get started.</p>
        <a href="{APP_URL}"
           style="display:inline-block; padding: 12px 24px; background-color: #4F8EF7;
                  color: #ffffff; text-decoration: none; border-radius: 6px; margin: 16px 0;">
            Start Using Replydesk AI
        </a>
        <p style="color: #666; font-size: 13px;">
            If you have any questions or feedback, use the Feedback page inside the app.
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;" />
        <p style="color: #999; font-size: 12px;">Replydesk AI — Your AI-powered assistant for professional communication</p>
    </body>
    </html>
    """
    body_text = (
        f"Welcome to Replydesk AI!\n\n"
        f"Your account is verified. You have 10 free generations per day.\n\n"
        f"Get started at: {APP_URL}\n\n"
        f"Tools available: Client Reply, Email Generator, Task Summary, Daily Report, "
        f"Meeting Notes, Follow-up Email, Tone Rewriter."
    )

    try:
        import boto3
        ses = boto3.client("ses", region_name=AWS_REGION)
        ses.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": body_text, "Charset": "UTF-8"},
                    "Html": {"Data": body_html, "Charset": "UTF-8"},
                },
            },
        )
        log.info("welcome_email_sent", extra={"email": email})
    except Exception as e:
        log.error("welcome_email_failed", extra={"email": email, "error": str(e)})


def resend_verification_email(email: str) -> tuple[bool, str]:
    """Resend the verification email for an unverified account."""
    email = email.lower()

    if not _is_valid_email(email):
        return False, "Please enter a valid email address."

    if _use_dynamodb():
        user = _load_user_dynamo(email)
    else:
        users = _load_users_json()
        user = users.get(email)

    if not user:
        return True, "If that email is registered, a verification link has been sent."

    if user.get("is_verified"):
        return False, "This account is already verified. You can log in."

    # Generate a fresh token
    token = secrets.token_urlsafe(32)
    user["verification_token"] = token
    _persist_user(user)

    _send_verification_email(email, token)
    log.info("verification_email_resent", extra={"email": email})
    return True, "Verification email resent. Please check your inbox."


def seed_default_users():
    """Seed the default admin user from environment variables if not already present."""
    admin_email = os.getenv("ADMIN_EMAIL", "").lower()
    admin_password = os.getenv("ADMIN_PASSWORD", "")

    if not admin_email or not admin_password:
        log.warning("seed_skipped", extra={"reason": "ADMIN_EMAIL or ADMIN_PASSWORD not set in environment"})
        return

    user_record = {
        "email": admin_email,
        "job_position": "Business Owner",
        "display_name": "Admin",
        "is_admin": True,
        "is_verified": True,
        "password_hash": _hash_password(admin_password),
    }

    if _use_dynamodb():
        if not _user_exists_dynamo(admin_email):
            _save_user_dynamo(user_record)
            log.info("admin_user_seeded", extra={"email": admin_email, "backend": "dynamodb"})
    else:
        users = _load_users_json()
        if admin_email not in users:
            users[admin_email] = user_record
            _save_users_json(users)
            log.info("admin_user_seeded", extra={"email": admin_email, "backend": "json"})


def login_user(email: str, password: str) -> tuple[bool, str]:
    """Authenticate a user by email. Returns (success, message).

    Tracks failed attempts and locks the account for LOCKOUT_DURATION_MINUTES
    after MAX_FAILED_LOGIN_ATTEMPTS consecutive failures.
    """
    if not email or not password:
        return False, "Please enter both email and password."

    if _use_dynamodb():
        user = _load_user_dynamo(email)
    else:
        users = _load_users_json()
        user = users.get(email.lower())

    if not user:
        return False, "Invalid email or password."

    # ── Email verification check ───────────────────────────────────────────
    if not user.get("is_verified", False):
        return False, "Please verify your email address before logging in. Check your inbox for the verification link."

    # ── Lockout check ──────────────────────────────────────────────────────
    lockout_until_str = user.get("lockout_until")
    if lockout_until_str:
        lockout_until = datetime.fromisoformat(lockout_until_str)
        if datetime.now() < lockout_until:
            remaining = int((lockout_until - datetime.now()).total_seconds() / 60) + 1
            log.warning("login_blocked_lockout", extra={"email": email, "remaining_minutes": remaining})
            return False, (
                f"Too many failed attempts. Account locked for {remaining} more minute(s)."
            )
        else:
            # Lockout expired — clear it
            user.pop("lockout_until", None)
            user.pop("failed_attempts", None)

    # ── Password check ─────────────────────────────────────────────────────
    if not _verify_password(password, user["password_hash"]):
        failed = user.get("failed_attempts", 0) + 1
        user["failed_attempts"] = failed

        if failed >= MAX_FAILED_LOGIN_ATTEMPTS:
            user["lockout_until"] = (
                datetime.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            ).isoformat()
            user["failed_attempts"] = 0
            _persist_user(user)
            log.warning("account_locked", extra={
                "email": email,
                "lockout_minutes": LOCKOUT_DURATION_MINUTES,
            })
            return False, (
                f"Too many failed attempts. Account locked for {LOCKOUT_DURATION_MINUTES} minutes."
            )

        _persist_user(user)
        attempts_left = MAX_FAILED_LOGIN_ATTEMPTS - failed
        log.warning("login_failed", extra={"email": email, "attempts_left": attempts_left})
        return False, f"Invalid email or password. {attempts_left} attempt(s) remaining."

    # ── Success — clear any failure counters ───────────────────────────────
    if user.get("failed_attempts") or user.get("lockout_until"):
        user.pop("failed_attempts", None)
        user.pop("lockout_until", None)
        _persist_user(user)

    log.info("login_success", extra={"email": email})
    return True, "Login successful!"


def _persist_user(user: dict):
    """Save a user record back to whichever backend is active."""
    if _use_dynamodb():
        _save_user_dynamo(user)
    else:
        users = _load_users_json()
        users[user["email"].lower()] = user
        _save_users_json(users)


def _get_user_profile(email: str) -> dict:
    """Get user profile data."""
    if _use_dynamodb():
        return _load_user_dynamo(email) or {}
    else:
        users = _load_users_json()
        return users.get(email.lower(), {})


def is_current_user_admin() -> bool:
    """Check if the currently logged-in user has admin privileges."""
    email = st.session_state.get("email", "")
    if not email:
        return False
    profile = _get_user_profile(email)
    return bool(profile.get("is_admin", False))


def logout():
    """Log out the current user."""
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.email = ""
    st.session_state.job_position = "Virtual Assistant"
    st.rerun()


# ─────────────────────────────────────────────
# Password Reset
# ─────────────────────────────────────────────

def _generate_reset_token() -> str:
    """Generate a secure URL-safe reset token."""
    return secrets.token_urlsafe(32)


def create_password_reset_token(email: str) -> tuple[bool, str]:
    """Create a reset token for the given email. Returns (success, token_or_message).

    Rate-limited to 1 request per 5 minutes per email to prevent inbox spam attacks.
    """
    email = email.lower()

    # ── Rate limit: 1 reset request per 5 minutes per email ───────────────
    if _use_dynamodb():
        user = _load_user_dynamo(email)
    else:
        users = _load_users_json()
        user = users.get(email)

    if not user:
        return True, ""  # Avoid enumeration

    last_reset_str = user.get("last_reset_request")
    if last_reset_str:
        try:
            last_reset = datetime.fromisoformat(last_reset_str)
            if datetime.now() - last_reset < timedelta(minutes=5):
                log.warning("reset_rate_limited", extra={"email": email})
                return True, ""  # Silently succeed to avoid enumeration
        except ValueError:
            pass

    token = _generate_reset_token()
    expiry = (datetime.now() + timedelta(minutes=RESET_TOKEN_EXPIRY_MINUTES)).isoformat()

    user["reset_token"] = token
    user["reset_token_expiry"] = expiry
    user["last_reset_request"] = datetime.now().isoformat()

    if _use_dynamodb():
        _save_user_dynamo(user)
    else:
        users = _load_users_json()
        users[email] = user
        _save_users_json(users)

    log.info("password_reset_token_created", extra={"email": email})
    return True, token


def validate_reset_token(token: str) -> tuple[bool, str]:
    """Validate a reset token. Returns (valid, email_or_error_message)."""
    if _use_dynamodb():
        table = _get_dynamodb_table()
        response = table.scan(
            FilterExpression="reset_token = :t",
            ExpressionAttributeValues={":t": token},
        )
        items = response.get("Items", [])
        user = items[0] if items else None
    else:
        users = _load_users_json()
        user = next(
            (u for u in users.values() if u.get("reset_token") == token),
            None,
        )

    if not user:
        return False, "Invalid or expired reset link."

    expiry_str = user.get("reset_token_expiry", "")
    if not expiry_str or datetime.now() > datetime.fromisoformat(expiry_str):
        return False, "This reset link has expired. Please request a new one."

    return True, user["email"]


def reset_password_with_token(token: str, new_password: str, confirm_password: str) -> tuple[bool, str]:
    """Reset a user's password using a valid token. Returns (success, message)."""
    valid, result = validate_reset_token(token)
    if not valid:
        return False, result

    email = result

    if len(new_password) < 6:
        return False, "Password must be at least 6 characters."
    if new_password != confirm_password:
        return False, "Passwords do not match."

    if _use_dynamodb():
        user = _load_user_dynamo(email)
    else:
        users = _load_users_json()
        user = users.get(email)

    if not user:
        return False, "User not found."

    user["password_hash"] = _hash_password(new_password)
    user.pop("reset_token", None)
    user.pop("reset_token_expiry", None)

    if _use_dynamodb():
        _save_user_dynamo(user)
    else:
        users = _load_users_json()
        users[email] = user
        _save_users_json(users)

    log.info("password_reset_success", extra={"email": email})
    return True, "Password reset successfully! You can now log in."


def send_reset_email(email: str, token: str) -> tuple[bool, str]:
    """Send a password reset email via AWS SES. Returns (success, message)."""
    reset_url = f"{APP_URL}?reset_token={token}"

    subject = "Reset your Replydesk AI password"
    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <img src="{APP_URL}/assets/logo-wide.svg" alt="Replydesk AI" style="height: 40px; margin-bottom: 24px;" />
        <h2 style="color: #1a1a2e;">Reset your password</h2>
        <p>We received a request to reset the password for your Replydesk AI account.</p>
        <p>Click the button below to choose a new password. This link expires in <strong>{RESET_TOKEN_EXPIRY_MINUTES} minutes</strong>.</p>
        <a href="{reset_url}"
           style="display:inline-block; padding: 12px 24px; background-color: #0f3460;
                  color: #ffffff; text-decoration: none; border-radius: 6px; margin: 16px 0;">
            Reset Password
        </a>
        <p style="color: #666; font-size: 13px;">
            If you didn't request this, you can safely ignore this email.<br/>
            This link will expire at {(datetime.now() + timedelta(minutes=RESET_TOKEN_EXPIRY_MINUTES)).strftime("%Y-%m-%d %H:%M UTC")}.
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;" />
        <p style="color: #999; font-size: 12px;">Replydesk AI — Your AI-powered assistant for professional communication</p>
    </body>
    </html>
    """
    body_text = (
        f"Reset your Replydesk AI password\n\n"
        f"Click the link below to reset your password (expires in {RESET_TOKEN_EXPIRY_MINUTES} minutes):\n\n"
        f"{reset_url}\n\n"
        f"If you didn't request this, ignore this email."
    )

    try:
        import boto3
        ses = boto3.client("ses", region_name=AWS_REGION)
        ses.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={"ToAddresses": [email]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": body_text, "Charset": "UTF-8"},
                    "Html": {"Data": body_html, "Charset": "UTF-8"},
                },
            },
        )
        return True, "Reset email sent."
    except Exception as e:
        log.error("ses_send_failed", extra={"email": email, "error": str(e)}, exc_info=True)
        return False, f"Failed to send email: {e}"


# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────

def render_auth_page():
    """Render the login/registration page. Returns True if authenticated."""
    init_auth_state()

    # Check session timeout
    if st.session_state.authenticated and _check_session_timeout():
        st.session_state.authenticated = False
        st.session_state.email = ""
        st.session_state.username = ""
        st.warning("⏰ Your session has expired due to inactivity. Please log in again.")

    if st.session_state.authenticated:
        _update_last_activity()
        return True

    # Back button to return to landing page
    if st.button("← Back to Home", key="back_to_landing_btn", type="secondary"):
        st.session_state.show_landing = True
        st.rerun()

    st.write("")

    # Center the form in a narrow column
    _, col, _ = st.columns([1, 1.4, 1])

    with col:
        st.image("assets/logo-wide.svg", use_container_width=True)
        # st.caption("Your AI-powered assistant for professional communication")
        st.write("")

        # Tabs for login and register
        tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

        with tab_login:
            login_email = st.text_input("Email Address", key="login_email", placeholder="you@example.com")
            login_password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")

            st.write("")
            if st.button("Log In", use_container_width=True, key="login_btn", type="primary"):
                success, message = login_user(login_email, login_password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.email = login_email
                    _update_last_activity()
                    user_data = _get_user_profile(login_email)
                    st.session_state.username = user_data.get("email", login_email)
                    st.session_state.job_position = user_data.get("job_position", "Virtual Assistant")
                    st.session_state.display_name = user_data.get("display_name", "")
                    st.session_state.is_admin = bool(user_data.get("is_admin", False))
                    # Load persisted generation count
                    today = datetime.now().strftime("%Y-%m-%d")
                    stored_date = user_data.get("rate_limit_date", "")
                    if stored_date == today:
                        st.session_state.generation_count = int(user_data.get("generation_count", 0))
                    else:
                        st.session_state.generation_count = 0
                    st.session_state.rate_limit_date = today
                    st.session_state.total_generations = int(user_data.get("total_generations", 0))
                    st.session_state._count_loaded = True
                    st.rerun()
                else:
                    st.error(message)
                    # Show resend button if account is unverified
                    if "verify your email" in message.lower():
                        st.session_state.show_resend = login_email

            if st.session_state.get("show_resend"):
                if st.button("📨 Resend Verification Email", use_container_width=True, key="resend_btn", type="secondary"):
                    ok, msg = resend_verification_email(st.session_state.show_resend)
                    if ok:
                        st.success(msg)
                        st.session_state.show_resend = None
                    else:
                        st.error(msg)

            if st.button("Forgot password?", use_container_width=True, key="forgot_pw_btn", type="secondary"):
                st.session_state.reset_flow = "request"
                st.rerun()

        with tab_register:
            reg_email = st.text_input("Email Address", key="reg_email", placeholder="you@example.com")
            reg_job = st.selectbox("Job Position", JOB_POSITIONS, key="reg_job")
            if reg_job == "Other":
                reg_job_other = st.text_input(
                    "Please specify your job position",
                    key="reg_job_other",
                    placeholder="e.g. Legal Assistant, Translator...",
                )
            else:
                reg_job_other = ""
            reg_password = st.text_input("Password", type="password", key="reg_password", placeholder="Min. 6 characters")
            reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="Repeat password")

            st.write("")
            if st.button("Create Account", use_container_width=True, key="register_btn", type="primary"):
                final_job = reg_job_other.strip() if reg_job == "Other" else reg_job
                if reg_job == "Other" and not reg_job_other.strip():
                    st.error("Please specify your job position.")
                else:
                    success, message = register_user(reg_email, final_job, reg_password, reg_confirm)
                    if success:
                        st.success(message)
                        st.info("👉 Switch to the **Login** tab to sign in.")
                    else:
                        st.error(message)

            st.caption(
                "By creating an account you agree to our "
                "[Privacy Policy](#)"
                " — click **Privacy Policy** below to read it."
            )
            if st.button("📄 Privacy Policy", use_container_width=True, key="reg_privacy_btn", type="secondary"):
                st.session_state.show_privacy_policy = True
                st.rerun()
            if st.button("📋 Terms of Service", use_container_width=True, key="reg_tos_btn", type="secondary"):
                st.session_state.show_tos = True
                st.rerun()

    return False
