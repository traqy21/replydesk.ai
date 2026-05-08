"""Replydesk AI — main application entry point with multi-page navigation."""

import streamlit as st

from config import APP_NAME, APP_CAPTION
from ui import init_session_state
from theme import apply_theme, get_logo
from auth import render_auth_page, logout, get_remaining_generations, seed_default_users, _get_user_profile
from profile import init_profile_state
from logger import get_logger
from session_manager import save_session, load_session, clear_session, inject_session_reader

log = get_logger("main")

# Page config
st.set_page_config(
    page_title=APP_NAME,
    layout="wide",
    page_icon="assets/logo.svg",
    initial_sidebar_state="collapsed",
)

# Initialize state
init_session_state()
init_profile_state()

# Seed default admin once per server process, not on every rerun
if "admin_seeded" not in st.session_state:
    seed_default_users()
    st.session_state.admin_seeded = True

# Apply theme early so landing page is also themed
apply_theme()

# ─────────────────────────────────────────────
# Session Restore — keep user logged in on refresh
# ─────────────────────────────────────────────
if not st.session_state.get("authenticated"):
    email = load_session()
    if email:
        user_data = _get_user_profile(email)
        if user_data and user_data.get("is_verified"):
            from datetime import datetime
            st.session_state.authenticated = True
            st.session_state.email = email
            st.session_state.username = email
            st.session_state.job_position = user_data.get("job_position", "Virtual Assistant")
            st.session_state.display_name = user_data.get("display_name", "")
            st.session_state.is_admin = bool(user_data.get("is_admin", False))
            st.session_state.show_landing = False
            today = datetime.now().strftime("%Y-%m-%d")
            stored_date = user_data.get("rate_limit_date", "")
            if stored_date == today:
                st.session_state.generation_count = int(user_data.get("generation_count", 0))
            else:
                st.session_state.generation_count = 0
            st.session_state.rate_limit_date = today
            st.session_state.total_generations = int(user_data.get("total_generations", 0))
            st.session_state._count_loaded = True
            st.session_state._session_checked = True
            log.info("session_restored", extra={"email": email})
            st.rerun()
        else:
            log.warning("session_restore_failed", extra={"email": email, "reason": "user not found or not verified"})

# ─────────────────────────────────────────────
# Password Reset Flow (via ?reset_token= param)
# ─────────────────────────────────────────────
reset_token = st.query_params.get("reset_token", "")
if reset_token or st.session_state.get("reset_flow") == "request":
    log.info("password_reset_flow_started", extra={"has_token": bool(reset_token)})
    from pages.reset_password import render as render_reset
    render_reset(token=reset_token)
    st.stop()

# ─────────────────────────────────────────────
# Email Verification Flow (via ?verify_token= param)
# ─────────────────────────────────────────────
verify_token = st.query_params.get("verify_token", "")
if verify_token:
    from pages.verify_email import render as render_verify
    render_verify(token=verify_token)
    st.stop()

# ─────────────────────────────────────────────
# Privacy Policy (accessible without login)
# ─────────────────────────────────────────────
if st.session_state.get("show_privacy_policy"):
    if st.button("← Back", key="privacy_back_btn", type="secondary"):
        st.session_state.show_privacy_policy = False
        st.rerun()
    from pages.privacy_policy import render as render_privacy
    render_privacy()
    st.stop()

# ─────────────────────────────────────────────
# Terms of Service (accessible without login)
# ─────────────────────────────────────────────
if st.session_state.get("show_tos"):
    if st.button("← Back", key="tos_back_btn", type="secondary"):
        st.session_state.show_tos = False
        st.rerun()
    from pages.terms_of_service import render as render_tos
    render_tos()
    st.stop()

# ─────────────────────────────────────────────
# Landing Page (unauthenticated visitors)
# ─────────────────────────────────────────────
if "show_landing" not in st.session_state:
    st.session_state.show_landing = True

if not st.session_state.get("authenticated") and st.session_state.show_landing:
    # Still inject session reader on landing page so refresh works
    if not st.session_state.get("_session_checked"):
        inject_session_reader()
        st.session_state._session_checked = True

    # Top nav bar for landing page
    nav_left, nav_right = st.columns([3, 1])
    with nav_left:
        st.image(get_logo(), width=160)
    with nav_right:
        if st.button("🔑 Log In / Register", use_container_width=True, key="nav_login_btn"):
            st.session_state.show_landing = False
            st.rerun()

    from pages.landing import render as render_landing
    render_landing()
    st.stop()

if "current_page" not in st.session_state:
    st.session_state.current_page = "Tools"

# Authentication gate
if not render_auth_page():
    st.stop()

# ─────────────────────────────────────────────
# Sidebar — Navigation + User info
# ─────────────────────────────────────────────

# Header
st.sidebar.image(get_logo(), use_container_width=True)

# Navigation (top priority — immediately accessible)
PAGES = ["🛠️ Tools", "📊 Dashboard", "📜 History", "💬 Feedback", "⚙️ Settings"]
if st.session_state.get("is_admin"):
    PAGES.append("🔐 Admin")

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

remaining = get_remaining_generations()
used = 50 - remaining
if used > 0:
    st.sidebar.caption(f"⚡ {remaining} generations remaining today")

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

st.sidebar.divider()
if st.sidebar.button("📄 Privacy Policy", use_container_width=True, type="secondary"):
    st.session_state.show_privacy_policy = True
    st.rerun()
if st.sidebar.button("📋 Terms of Service", use_container_width=True, type="secondary"):
    st.session_state.show_tos = True
    st.rerun()

# ─────────────────────────────────────────────
# Main Content — Page Router
# ─────────────────────────────────────────────

if st.session_state.current_page == "Tools":
    from pages.tools import render
    render()

elif st.session_state.current_page == "Dashboard":
    from pages.dashboard import render
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
