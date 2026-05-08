"""Email verification page — handles ?verify_token= links."""

import streamlit as st
from auth import verify_email_token


def render(token: str):
    """Render the email verification result page."""
    from theme import get_logo
    st.image(get_logo(), use_container_width=False, width=300)
    st.write("")

    _, col, _ = st.columns([1, 1.4, 1])

    with col:
        with st.spinner("Verifying your email..."):
            success, message = verify_email_token(token)

        if success:
            st.success(f"✅ {message}")
            st.balloons()
        else:
            st.error(f"⛔ {message}")
            st.caption("The link may have already been used or is invalid. Try registering again.")

        st.write("")
        if st.button("→ Go to Login", use_container_width=True, type="primary", key="verify_go_login"):
            st.query_params.clear()
            st.session_state.show_landing = False
            st.rerun()
