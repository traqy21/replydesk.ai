"""Authentication module — login and registration with JSON file storage."""

import streamlit as st
import json
import hashlib
import os

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")


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


def init_auth_state():
    """Initialize authentication session state."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "auth_page" not in st.session_state:
        st.session_state.auth_page = "login"


def register_user(username: str, password: str, confirm_password: str) -> tuple[bool, str]:
    """Register a new user. Returns (success, message)."""
    if not username or not password:
        return False, "Username and password are required."

    if len(username) < 3:
        return False, "Username must be at least 3 characters."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    if password != confirm_password:
        return False, "Passwords do not match."

    users = _load_users()

    if username.lower() in users:
        return False, "Username already exists."

    users[username.lower()] = {
        "username": username,
        "password_hash": _hash_password(password),
    }
    _save_users(users)
    return True, "Registration successful! You can now log in."


def login_user(username: str, password: str) -> tuple[bool, str]:
    """Authenticate a user. Returns (success, message)."""
    if not username or not password:
        return False, "Please enter both username and password."

    users = _load_users()

    user = users.get(username.lower())
    if not user:
        return False, "Invalid username or password."

    if user["password_hash"] != _hash_password(password):
        return False, "Invalid username or password."

    return True, "Login successful!"


def logout():
    """Log out the current user."""
    st.session_state.authenticated = False
    st.session_state.username = ""
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
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Log In", use_container_width=True, key="login_btn"):
            success, message = login_user(login_username, login_password)
            if success:
                st.session_state.authenticated = True
                st.session_state.username = login_username
                st.rerun()
            else:
                st.error(message)

    with tab_register:
        st.subheader("Create an account")
        reg_username = st.text_input("Username", key="reg_username")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

        if st.button("Register", use_container_width=True, key="register_btn"):
            success, message = register_user(reg_username, reg_password, reg_confirm)
            if success:
                st.success(message)
            else:
                st.error(message)

    return False
