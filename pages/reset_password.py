"""Password reset page — request and confirm password reset via email."""

import streamlit as st
from auth import (
    create_password_reset_token,
    send_reset_email,
    validate_reset_token,
    reset_password_with_token,
    _is_valid_email,
)


def render_request_form():
    """Render the 'forgot password' form where users enter their email."""
    st.markdown("#### 🔑 Forgot Password")
    st.caption("Enter your email address and we'll send you a reset link")

    st.divider()

    email = st.text_input("Email Address", placeholder="you@example.com", key="reset_email_input")

    if st.button("📨 Send Reset Link", use_container_width=True, key="send_reset_btn"):
        if not email:
            st.error("Please enter your email address.")
        elif not _is_valid_email(email):
            st.error("Please enter a valid email address.")
        else:
            with st.spinner("Sending reset email..."):
                success, token = create_password_reset_token(email)

                if success and token:
                    email_sent, msg = send_reset_email(email, token)
                    if email_sent:
                        st.success(
                            "✅ If that email is registered, you'll receive a reset link shortly. "
                            "Check your inbox (and spam folder)."
                        )
                    else:
                        st.error(f"Could not send email: {msg}")
                else:
                    # No token means email not found — show same message to avoid enumeration
                    st.success(
                        "✅ If that email is registered, you'll receive a reset link shortly. "
                        "Check your inbox (and spam folder)."
                    )

    st.divider()

    if st.button("← Back to Login", use_container_width=True, key="back_to_login_btn", type="secondary"):
        st.session_state.reset_flow = None
        st.rerun()


def render_reset_form(token: str):
    """Render the new password form after clicking the reset link."""
    # Validate token first
    valid, result = validate_reset_token(token)

    if not valid:
        st.error(f"⛔ {result}")
        st.divider()
        if st.button("← Back to Login", use_container_width=True, type="secondary"):
            st.session_state.reset_flow = None
            st.query_params.clear()
            st.rerun()
        return

    email = result

    st.markdown("#### 🔒 Set New Password")
    st.caption(f"Resetting password for **{email}**")
    st.divider()

    new_password = st.text_input("New Password", type="password", key="new_pw_input")
    confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_pw_input")

    if st.button("✅ Reset Password", use_container_width=True, key="confirm_reset_btn"):
        success, message = reset_password_with_token(token, new_password, confirm_password)
        if success:
            st.success(f"✅ {message}")
            st.info("👉 You can now log in with your new password.")
            # Clear the token from URL
            st.query_params.clear()
            if st.button("→ Go to Login", use_container_width=True, key="go_login_btn"):
                st.session_state.reset_flow = None
                st.rerun()
        else:
            st.error(message)


def render(token: str = ""):
    """Render the appropriate reset page based on whether a token is present."""
    from theme import get_logo
    st.image(get_logo(), use_container_width=False, width=300)

    if token:
        render_reset_form(token)
    else:
        render_request_form()
