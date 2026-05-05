"""Admin page — view registered users and usage stats."""

import streamlit as st
from auth import _use_dynamodb, _load_users_json, _get_dynamodb_table

# Admin email(s) — only these users can access the admin page
ADMIN_EMAILS = ["admin@replydesk.ai"]


def _is_admin() -> bool:
    """Check if the current user is an admin."""
    return st.session_state.get("email", "").lower() in ADMIN_EMAILS


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


def render():
    """Render the admin page."""
    st.markdown("#### 🔐 Admin Panel")

    if not _is_admin():
        st.error("⛔ Access denied. This page is restricted to administrators.")
        return

    st.caption("Manage users and view system information")
    st.divider()

    users = _load_all_users()

    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Registered Users", len(users))
    with col2:
        positions = set(u.get("job_position", "Unknown") for u in users.values())
        st.metric("Job Positions", len(positions))
    with col3:
        st.metric("Storage Backend", "DynamoDB" if _use_dynamodb() else "JSON File")

    st.divider()

    # User list
    st.markdown("**Registered Users**")

    if not users:
        st.info("No users registered yet.")
        return

    # Display as a table
    user_data = []
    for email, data in users.items():
        user_data.append({
            "Email": data.get("email", email),
            "Display Name": data.get("display_name", "—"),
            "Job Position": data.get("job_position", "—"),
        })

    st.dataframe(user_data, use_container_width=True, hide_index=True)

    st.divider()

    # System info
    st.markdown("**System Information**")
    import os
    st.json({
        "storage_backend": "DynamoDB" if _use_dynamodb() else "JSON File",
        "dynamodb_table": os.getenv("DYNAMODB_TABLE", "Not configured"),
        "aws_region": os.getenv("AWS_REGION", "us-east-1"),
        "total_users": len(users),
    })
