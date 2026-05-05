"""Admin page — overview, user management, feedback, and system info."""

import os
from collections import Counter
from datetime import datetime

import streamlit as st

from auth import (
    _use_dynamodb,
    _load_users_json,
    _save_users_json,
    _get_dynamodb_table,
    _hash_password,
    is_current_user_admin,
    MAX_GENERATIONS_PER_DAY,
)
from feedback_store import load_all_feedback


# ─────────────────────────────────────────────
# Data helpers
# ─────────────────────────────────────────────

def _load_all_users() -> dict:
    if _use_dynamodb():
        table = _get_dynamodb_table()
        response = table.scan()
        users = {}
        for item in response.get("Items", []):
            users[item["email"]] = item
        return users
    return _load_users_json()


def _set_admin_flag(email: str, value: bool):
    email = email.lower()
    if _use_dynamodb():
        _get_dynamodb_table().update_item(
            Key={"email": email},
            UpdateExpression="SET is_admin = :v",
            ExpressionAttributeValues={":v": value},
        )
    else:
        users = _load_users_json()
        if email in users:
            users[email]["is_admin"] = value
            _save_users_json(users)


def _set_locked_flag(email: str, locked: bool):
    """Manually lock or unlock a user account."""
    email = email.lower()
    if _use_dynamodb():
        if locked:
            _get_dynamodb_table().update_item(
                Key={"email": email},
                UpdateExpression="SET lockout_until = :v",
                ExpressionAttributeValues={":v": "9999-12-31T23:59:59"},
            )
        else:
            _get_dynamodb_table().update_item(
                Key={"email": email},
                UpdateExpression="REMOVE lockout_until, failed_attempts",
            )
    else:
        users = _load_users_json()
        if email in users:
            if locked:
                users[email]["lockout_until"] = "9999-12-31T23:59:59"
            else:
                users[email].pop("lockout_until", None)
                users[email].pop("failed_attempts", None)
            _save_users_json(users)


def _reset_user_password(email: str, new_password: str):
    """Force-reset a user's password."""
    email = email.lower()
    hashed = _hash_password(new_password)
    if _use_dynamodb():
        _get_dynamodb_table().update_item(
            Key={"email": email},
            UpdateExpression="SET password_hash = :v REMOVE reset_token, reset_token_expiry",
            ExpressionAttributeValues={":v": hashed},
        )
    else:
        users = _load_users_json()
        if email in users:
            users[email]["password_hash"] = hashed
            users[email].pop("reset_token", None)
            users[email].pop("reset_token_expiry", None)
            _save_users_json(users)


def _is_locked(user: dict) -> bool:
    lockout = user.get("lockout_until", "")
    if not lockout:
        return False
    try:
        return datetime.now() < datetime.fromisoformat(lockout)
    except ValueError:
        return False


# ─────────────────────────────────────────────
# Tab renderers
# ─────────────────────────────────────────────

def _render_overview(users: dict, feedback: list):
    """Overview tab — key metrics and charts."""
    total = len(users)
    admins = sum(1 for u in users.values() if u.get("is_admin"))
    locked = sum(1 for u in users.values() if _is_locked(u))
    total_feedback = len(feedback)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Users", total)
    c2.metric("Admins", admins)
    c3.metric("Locked Accounts", locked)
    c4.metric("Feedback Entries", total_feedback)

    st.divider()

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("**Users by Job Position**")
        position_counts = Counter(
            u.get("job_position", "Unknown") for u in users.values()
        )
        if position_counts:
            st.bar_chart(dict(position_counts))
        else:
            st.caption("No data yet.")

    with right:
        st.markdown("**Feedback by Category**")
        category_counts = Counter(f.get("category", "Unknown") for f in feedback)
        if category_counts:
            st.bar_chart(dict(category_counts))
        else:
            st.caption("No feedback yet.")

    st.divider()

    st.markdown("**Recent Registrations**")
    # Users don't store created_at yet — show last 5 alphabetically as a fallback
    recent = list(users.values())[-5:]
    if recent:
        rows = [
            {
                "Email": u.get("email", "—"),
                "Display Name": u.get("display_name", "—"),
                "Job Position": u.get("job_position", "—"),
                "Role": "🔐 Admin" if u.get("is_admin") else "User",
            }
            for u in reversed(recent)
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.caption("No users yet.")


def _render_users(users: dict):
    """Users tab — full user table with management actions."""
    current_email = st.session_state.get("email", "").lower()

    # Search / filter
    search = st.text_input("🔍 Search by email or name", placeholder="Type to filter...", key="admin_search")
    col_filter, _ = st.columns([1, 3])
    with col_filter:
        role_filter = st.selectbox("Role", ["All", "Admin", "User", "Locked"], key="admin_role_filter")

    filtered = {
        e: u for e, u in users.items()
        if (
            search.lower() in e.lower()
            or search.lower() in u.get("display_name", "").lower()
        ) and (
            role_filter == "All"
            or (role_filter == "Admin" and u.get("is_admin"))
            or (role_filter == "User" and not u.get("is_admin") and not _is_locked(u))
            or (role_filter == "Locked" and _is_locked(u))
        )
    }

    st.caption(f"Showing {len(filtered)} of {len(users)} users")
    st.divider()

    if not filtered:
        st.info("No users match the current filter.")
        return

    # Column headers
    h1, h2, h3, h4, h5, h6 = st.columns([2.2, 1.4, 1.8, 0.9, 1.3, 1.3])
    h1.markdown("**Email**")
    h2.markdown("**Name**")
    h3.markdown("**Position**")
    h4.markdown("**Role**")
    h5.markdown("**Status**")
    h6.markdown("**Actions**")
    st.divider()

    for email, data in filtered.items():
        is_self = email.lower() == current_email
        user_is_admin = bool(data.get("is_admin", False))
        locked = _is_locked(data)

        c1, c2, c3, c4, c5, c6 = st.columns([2.2, 1.4, 1.8, 0.9, 1.3, 1.3])

        with c1:
            st.caption(data.get("email", email))
        with c2:
            st.caption(data.get("display_name") or "—")
        with c3:
            st.caption(data.get("job_position", "—"))
        with c4:
            st.caption("🔐 Admin" if user_is_admin else "User")
        with c5:
            if is_self:
                st.caption("_(you)_")
            elif locked:
                st.markdown("🔴 Locked")
            else:
                st.markdown("🟢 Active")
        with c6:
            if not is_self:
                with st.popover("⚙️", use_container_width=True):
                    st.markdown(f"**Manage:** `{email}`")
                    st.divider()

                    # Admin toggle
                    if user_is_admin:
                        if st.button("Revoke Admin", key=f"rev_{email}", use_container_width=True):
                            _set_admin_flag(email, False)
                            st.success("Admin revoked.")
                            st.rerun()
                    else:
                        if st.button("Make Admin", key=f"grant_{email}", use_container_width=True, type="primary"):
                            _set_admin_flag(email, True)
                            st.success("Admin granted.")
                            st.rerun()

                    # Lock / unlock
                    if locked:
                        if st.button("🔓 Unlock Account", key=f"unlock_{email}", use_container_width=True):
                            _set_locked_flag(email, False)
                            st.success("Account unlocked.")
                            st.rerun()
                    else:
                        if st.button("🔒 Lock Account", key=f"lock_{email}", use_container_width=True):
                            _set_locked_flag(email, True)
                            st.warning("Account locked.")
                            st.rerun()

                    # Force password reset
                    st.divider()
                    new_pw = st.text_input("New Password", type="password", key=f"pw_{email}", placeholder="Min. 6 chars")
                    if st.button("🔑 Reset Password", key=f"resetpw_{email}", use_container_width=True):
                        if len(new_pw) < 6:
                            st.error("Password must be at least 6 characters.")
                        else:
                            _reset_user_password(email, new_pw)
                            st.success("Password updated.")


def _render_feedback(feedback: list):
    """Feedback tab — all submitted feedback with filters."""
    if not feedback:
        st.info("No feedback submitted yet.")
        return

    # Filters
    fc1, fc2 = st.columns(2)
    with fc1:
        categories = ["All"] + sorted(set(f.get("category", "Other") for f in feedback))
        cat_filter = st.selectbox("Category", categories, key="fb_cat_filter")
    with fc2:
        ratings = ["All"] + sorted(set(f.get("rating", "") for f in feedback), reverse=True)
        rat_filter = st.selectbox("Rating", ratings, key="fb_rat_filter")

    filtered = [
        f for f in feedback
        if (cat_filter == "All" or f.get("category") == cat_filter)
        and (rat_filter == "All" or f.get("rating") == rat_filter)
    ]

    st.caption(f"Showing {len(filtered)} of {len(feedback)} entries")
    st.divider()

    for entry in reversed(filtered):
        with st.expander(
            f"**{entry.get('category', '—')}** — {entry.get('subject', '—')}  ·  "
            f"{entry.get('rating', '')}  ·  {entry.get('timestamp', '')}",
            expanded=False,
        ):
            st.caption(f"From: {entry.get('email', 'anonymous')}")
            st.markdown(f"**Message:** {entry.get('message', '—')}")


def _render_system(users: dict):
    """System tab — infrastructure info."""
    st.markdown("**Environment**")
    st.json({
        "storage_backend": "DynamoDB" if _use_dynamodb() else "JSON File",
        "dynamodb_users_table": os.getenv("DYNAMODB_TABLE", "Not configured"),
        "dynamodb_feedback_table": f"{os.getenv('APP_NAME', 'replydesk-ai')}-feedback",
        "aws_region": os.getenv("AWS_REGION", "us-east-1"),
        "log_group": "/replydesk-ai/app",
        "total_users": len(users),
        "total_admins": sum(1 for u in users.values() if u.get("is_admin")),
        "daily_generation_limit": MAX_GENERATIONS_PER_DAY,
    })


# ─────────────────────────────────────────────
# Main render
# ─────────────────────────────────────────────

def render():
    """Render the admin panel."""
    st.markdown("#### 🔐 Admin Panel")

    if not st.session_state.get("is_admin") and not is_current_user_admin():
        st.error("⛔ Access denied. This page is restricted to administrators.")
        return

    users = _load_all_users()
    feedback = load_all_feedback()

    tab_overview, tab_users, tab_feedback, tab_system = st.tabs([
        "📊 Overview", "👥 Users", "💬 Feedback", "⚙️ System"
    ])

    with tab_overview:
        _render_overview(users, feedback)

    with tab_users:
        _render_users(users)

    with tab_feedback:
        _render_feedback(feedback)

    with tab_system:
        _render_system(users)
