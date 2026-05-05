"""Admin page — user management and system information."""

import os
import streamlit as st
from auth import (
    _use_dynamodb,
    _load_users_json,
    _save_users_json,
    _get_dynamodb_table,
    _save_user_dynamo,
    is_current_user_admin,
)


def _load_all_users() -> dict:
    """Load all users from storage."""
    if _use_dynamodb():
        table = _get_dynamodb_table()
        response = table.scan()
        users = {}
        for item in response.get("Items", []):
            users[item["email"]] = item
        return users
    else:
        return _load_users_json()


def _set_admin_flag(email: str, is_admin: bool):
    """Grant or revoke admin privileges for a user."""
    email = email.lower()
    if _use_dynamodb():
        table = _get_dynamodb_table()
        table.update_item(
            Key={"email": email},
            UpdateExpression="SET is_admin = :val",
            ExpressionAttributeValues={":val": is_admin},
        )
    else:
        users = _load_users_json()
        if email in users:
            users[email]["is_admin"] = is_admin
            _save_users_json(users)


def render():
    """Render the admin page."""
    st.markdown("#### 🔐 Admin Panel")

    if not st.session_state.get("is_admin") and not is_current_user_admin():
        st.error("⛔ Access denied. This page is restricted to administrators.")
        return

    st.caption("Manage users and view system information")
    st.divider()

    users = _load_all_users()

    # ── Stats ──────────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Registered Users", len(users))
    with col2:
        admin_count = sum(1 for u in users.values() if u.get("is_admin"))
        st.metric("Admins", admin_count)
    with col3:
        positions = set(u.get("job_position", "Unknown") for u in users.values())
        st.metric("Job Positions", len(positions))
    with col4:
        st.metric("Storage Backend", "DynamoDB" if _use_dynamodb() else "JSON File")

    st.divider()

    # ── User management table ──────────────────────────────────────────────
    st.markdown("**Registered Users**")

    if not users:
        st.info("No users registered yet.")
        return

    current_email = st.session_state.get("email", "").lower()

    for email, data in users.items():
        user_is_admin = bool(data.get("is_admin", False))
        is_self = email.lower() == current_email

        col_email, col_name, col_job, col_role, col_action = st.columns([2.5, 1.5, 2, 1, 1.2])

        with col_email:
            st.caption(data.get("email", email))
        with col_name:
            st.caption(data.get("display_name", "—"))
        with col_job:
            st.caption(data.get("job_position", "—"))
        with col_role:
            if user_is_admin:
                st.markdown("🔐 **Admin**")
            else:
                st.caption("User")
        with col_action:
            if is_self:
                st.caption("_(you)_")
            elif user_is_admin:
                if st.button("Revoke", key=f"revoke_{email}", use_container_width=True):
                    _set_admin_flag(email, False)
                    st.success(f"Admin revoked for {email}")
                    st.rerun()
            else:
                if st.button("Make Admin", key=f"grant_{email}", use_container_width=True, type="primary"):
                    _set_admin_flag(email, True)
                    st.success(f"{email} is now an admin.")
                    st.rerun()

    st.divider()

    # ── System info ────────────────────────────────────────────────────────
    st.markdown("**System Information**")
    st.json({
        "storage_backend": "DynamoDB" if _use_dynamodb() else "JSON File",
        "dynamodb_users_table": os.getenv("DYNAMODB_TABLE", "Not configured"),
        "dynamodb_feedback_table": f"{os.getenv('APP_NAME', 'replydesk-ai')}-feedback",
        "aws_region": os.getenv("AWS_REGION", "us-east-1"),
        "total_users": len(users),
        "total_admins": admin_count,
    })
