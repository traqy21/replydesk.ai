"""User profile/settings page — update display name, job position, and password."""

import streamlit as st
from auth import (
    JOB_POSITIONS,
    _hash_password,
    _verify_password,
    _use_dynamodb,
    _load_users_json,
    _save_users_json,
    _load_user_dynamo,
    _save_user_dynamo,
)


def init_profile_state():
    """Initialize profile-related session state."""
    if "display_name" not in st.session_state:
        st.session_state.display_name = ""


def _get_current_user() -> dict:
    """Get the current user's data from storage."""
    email = st.session_state.email
    if _use_dynamodb():
        return _load_user_dynamo(email) or {}
    else:
        users = _load_users_json()
        return users.get(email.lower(), {})


def _save_current_user(user_data: dict):
    """Save updated user data to storage."""
    if _use_dynamodb():
        _save_user_dynamo(user_data)
    else:
        users = _load_users_json()
        users[user_data["email"].lower()] = user_data
        _save_users_json(users)


def render_profile_page():
    """Render the profile/settings page in a dialog-like expander."""
    user_data = _get_current_user()

    st.markdown("#### ⚙️ Profile Settings")
    st.caption("Update your account information")

    st.divider()

    # ─── Display Name ───
    st.markdown("**Display Name**")
    current_display_name = user_data.get("display_name", "")
    new_display_name = st.text_input(
        "Display Name",
        value=current_display_name,
        placeholder="Enter a display name",
        label_visibility="collapsed",
        key="profile_display_name",
    )

    # ─── Job Position ───
    st.markdown("**Job Position**")
    current_job = user_data.get("job_position", "Virtual Assistant")

    # If saved value isn't in the list, it's a custom "Other" value
    if current_job in JOB_POSITIONS and current_job != "Other":
        current_index = JOB_POSITIONS.index(current_job)
        current_other = ""
    else:
        current_index = JOB_POSITIONS.index("Other")
        current_other = current_job if current_job not in JOB_POSITIONS else ""

    new_job = st.selectbox(
        "Job Position",
        JOB_POSITIONS,
        index=current_index,
        label_visibility="collapsed",
        key="profile_job_position",
    )

    if new_job == "Other":
        new_job_other = st.text_input(
            "Please specify your job position",
            value=current_other,
            placeholder="e.g. Legal Assistant, Translator...",
            key="profile_job_other",
        )
    else:
        new_job_other = ""

    # Save profile button
    if st.button("💾 Save Profile", use_container_width=True, key="save_profile_btn"):
        final_job = new_job_other.strip() if new_job == "Other" else new_job
        if new_job == "Other" and not new_job_other.strip():
            st.error("Please specify your job position.")
        else:
            user_data["display_name"] = new_display_name
            user_data["job_position"] = final_job
            _save_current_user(user_data)

            st.session_state.job_position = final_job
            st.session_state.display_name = new_display_name
            st.success("Profile updated successfully!")

    st.divider()

    # ─── Change Password ───
    st.markdown("**Change Password**")
    current_password = st.text_input(
        "Current Password", type="password", key="profile_current_pw"
    )
    new_password = st.text_input(
        "New Password", type="password", key="profile_new_pw"
    )
    confirm_password = st.text_input(
        "Confirm New Password", type="password", key="profile_confirm_pw"
    )

    if st.button("🔒 Update Password", use_container_width=True, key="update_pw_btn"):
        if not current_password or not new_password or not confirm_password:
            st.error("Please fill in all password fields.")
        elif not _verify_password(current_password, user_data.get("password_hash", "")):
            st.error("Current password is incorrect.")
        elif len(new_password) < 6:
            st.error("New password must be at least 6 characters.")
        elif new_password != confirm_password:
            st.error("New passwords do not match.")
        else:
            user_data["password_hash"] = _hash_password(new_password)
            _save_current_user(user_data)
            st.success("Password updated successfully!")
