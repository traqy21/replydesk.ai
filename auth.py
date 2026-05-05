"""Authentication module — login and registration with JSON file storage."""

import streamlit as st
import json
import hashlib
import os
import re

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

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


def _load_users() -> dict:
    """Load users from the JSON file."""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def _save_users(users: dict):
    """Save users to the JSON file."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def _hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def _is_valid_email(email: str) -> bool:
    """Check if the email format is valid."""
    return bool(email and re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))


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


def register_user(email: str, job_position: str, password: str, confirm_password: str) -> tuple[bool, str]:
    """Register a new user using email as the identifier. Returns (success, message)."""
    if not _is_valid_email(email):
        return False, "Please enter a valid email address."

    if not job_position:
        return False, "Please select a job position."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    if password != confirm_password:
        return False, "Passwords do not match."

    users = _load_users()

    if email.lower() in users:
        return False, "This email is already registered."

    users[email.lower()] = {
        "email": email,
        "job_position": job_position,
        "password_hash": _hash_password(password),
    }
    _save_users(users)
    return True, "Registration successful! You can now log in."


def login_user(email: str, password: str) -> tuple[bool, str]:
    """Authenticate a user by email. Returns (success, message)."""
    if not email or not password:
        return False, "Please enter both email and password."

    users = _load_users()

    user = users.get(email.lower())
    if not user:
        return False, "Invalid email or password."

    if user["password_hash"] != _hash_password(password):
        return False, "Invalid email or password."

    return True, "Login successful!"


def logout():
    """Log out the current user."""
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.email = ""
    st.session_state.job_position = "Virtual Assistant"
    st.rerun()


def render_auth_page():
    """Render the login/registration page. Returns True if authenticated."""
    init_auth_state()

    if st.session_state.authenticated:
        return True

    st.title("💻 Replydesk AI")
    st.caption("Generate emails, replies, and reports instantly")

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
                # Load user profile into session
                users = _load_users()
                user_data = users.get(login_email.lower(), {})
                st.session_state.username = user_data.get("email", login_email)
                st.session_state.job_position = user_data.get("job_position", "Virtual Assistant")
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
