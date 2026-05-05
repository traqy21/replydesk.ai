"""Authentication module — supports JSON file (local) and DynamoDB (production).

Features:
- Bcrypt password hashing
- Session timeout (auto-logout after inactivity)
- Rate limiting on generations
"""

import streamlit as st
import json
import os
import re
from datetime import datetime, timedelta

import bcrypt

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Session timeout in minutes
SESSION_TIMEOUT_MINUTES = 30

# Rate limiting: max generations per day per user
MAX_GENERATIONS_PER_DAY = 50

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
# Rate Limiting
# ─────────────────────────────────────────────

def check_rate_limit() -> tuple[bool, str]:
    """Check if the user has exceeded the daily generation limit.
    Returns (allowed, message).
    """
    today = datetime.now().strftime("%Y-%m-%d")

    # Reset counter if it's a new day
    if st.session_state.get("rate_limit_date") != today:
        st.session_state.rate_limit_date = today
        st.session_state.generation_count = 0

    if st.session_state.generation_count >= MAX_GENERATIONS_PER_DAY:
        remaining_msg = "You've reached your daily limit of {} generations. Try again tomorrow.".format(
            MAX_GENERATIONS_PER_DAY
        )
        return False, remaining_msg

    return True, ""


def increment_generation_count():
    """Increment the daily generation counter."""
    st.session_state.generation_count = st.session_state.get("generation_count", 0) + 1


def get_remaining_generations() -> int:
    """Get the number of remaining generations for today."""
    return MAX_GENERATIONS_PER_DAY - st.session_state.get("generation_count", 0)


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

    user_data = {
        "email": email.lower(),
        "job_position": job_position,
        "password_hash": _hash_password(password),
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

    return True, "Registration successful! You can now log in."


def login_user(email: str, password: str) -> tuple[bool, str]:
    """Authenticate a user by email. Returns (success, message)."""
    if not email or not password:
        return False, "Please enter both email and password."

    if _use_dynamodb():
        user = _load_user_dynamo(email)
    else:
        users = _load_users_json()
        user = users.get(email.lower())

    if not user:
        return False, "Invalid email or password."

    if not _verify_password(password, user["password_hash"]):
        return False, "Invalid email or password."

    return True, "Login successful!"


def _get_user_profile(email: str) -> dict:
    """Get user profile data."""
    if _use_dynamodb():
        return _load_user_dynamo(email) or {}
    else:
        users = _load_users_json()
        return users.get(email.lower(), {})


def logout():
    """Log out the current user."""
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.email = ""
    st.session_state.job_position = "Virtual Assistant"
    st.rerun()


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

    st.image("assets/logo-wide.svg", use_container_width=False, width=300)
    st.caption("Your AI-powered assistant for professional communication")

    # Tabs for login and register
    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

    with tab_login:
        st.subheader("Welcome back")
        login_email = st.text_input("Email Address", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Log In", use_container_width=True, key="login_btn"):
            success, message = login_user(login_email, login_password)
            if success:
                st.session_state.authenticated = True
                st.session_state.email = login_email
                _update_last_activity()
                # Load user profile into session
                user_data = _get_user_profile(login_email)
                st.session_state.username = user_data.get("email", login_email)
                st.session_state.job_position = user_data.get("job_position", "Virtual Assistant")
                st.session_state.display_name = user_data.get("display_name", "")
                st.rerun()
            else:
                st.error(message)

    with tab_register:
        st.subheader("Create an account")
        reg_email = st.text_input("Email Address", key="reg_email")
        reg_job = st.selectbox("Job Position", JOB_POSITIONS, key="reg_job")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

        if st.button("Register", use_container_width=True, key="register_btn"):
            success, message = register_user(reg_email, reg_job, reg_password, reg_confirm)
            if success:
                st.success(message)
                st.info("👉 Switch to the **Login** tab above to sign in.")
            else:
                st.error(message)

    return False
