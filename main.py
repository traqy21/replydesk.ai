"""Replydesk AI — main application entry point with multi-page navigation."""

import streamlit as st

from config import APP_NAME, APP_CAPTION
from ui import init_session_state
from theme import apply_theme
from auth import render_auth_page, logout, get_remaining_generations, seed_default_users
from profile import init_profile_state
from logger import get_logger

log = get_logger("main")

# Page config
st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="assets/logo.svg")

# Initialize state
init_session_state()
init_profile_state()
seed_default_users()

# ─────────────────────────────────────────────
# Password Reset Flow (via ?reset_token= param)
# ─────────────────────────────────────────────
reset_token = st.query_params.get("reset_token", "")
if reset_token or st.session_state.get("reset_flow") == "request":
    log.info("password_reset_flow_started", extra={"has_token": bool(reset_token)})
    from pages.reset_password import render as render_reset
    render_reset(token=reset_token)
    st.stop()

if "current_page" not in st.session_state:
    st.session_state.current_page = "Tools"

# Apply theme
apply_theme()

# Authentication gate
if not render_auth_page():
    st.stop()

# ─────────────────────────────────────────────
# Sidebar — Navigation + User info
# ─────────────────────────────────────────────

# Header
st.sidebar.image("assets/logo-wide.svg", use_container_width=True)

# Navigation (top priority — immediately accessible)
PAGES = ["🛠️ Tools", "📜 History", "💬 Feedback", "⚙️ Settings", "🔐 Admin"]

for page_label in PAGES:
    page_name = page_label.split(" ", 1)[1]
    if st.sidebar.button(
        page_label,
        use_container_width=True,
        key=f"nav_{page_name}",
        type="primary" if st.session_state.current_page == page_name else "secondary",
    ):
        st.session_state.current_page = page_name
        st.rerun()

st.sidebar.divider()

# User info
display = st.session_state.display_name or st.session_state.email
st.sidebar.markdown(f"👤 **{display}**")
st.sidebar.caption(f"📋 {st.session_state.job_position}")
st.sidebar.caption(f"⚡ {get_remaining_generations()} remaining today")

st.sidebar.divider()

# Theme toggle
st.sidebar.subheader("🎨 Theme")
theme = st.sidebar.radio(
    "Choose theme",
    ["Light", "Dark"],
    index=0 if st.session_state.theme == "Light" else 1,
    horizontal=True,
    label_visibility="collapsed",
)
if theme != st.session_state.theme:
    st.session_state.theme = theme
    st.rerun()

st.sidebar.divider()

# Logout
if st.sidebar.button("🚪 Logout", use_container_width=True):
    logout()

# ─────────────────────────────────────────────
# Main Content — Page Router
# ─────────────────────────────────────────────

if st.session_state.current_page == "Tools":
    from pages.tools import render
    render()

elif st.session_state.current_page == "History":
    from pages.history import render
    render()

elif st.session_state.current_page == "Settings":
    from pages.settings import render
    render()

elif st.session_state.current_page == "Feedback":
    from pages.feedback import render
    render()

elif st.session_state.current_page == "Admin":
    from pages.admin import render
    render()
