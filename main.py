"""Replydesk AI — main application entry point."""

import streamlit as st

from config import APP_NAME, APP_CAPTION, MODEL, client
from prompts import build_prompt
from ui import (
    init_session_state,
    render_sidebar,
    render_input,
    render_output,
    render_progress,
    add_to_history,
)
from theme import apply_theme
from auth import render_auth_page, logout

# Page config
st.set_page_config(page_title=APP_NAME, layout="wide")

# Initialize state
init_session_state()

# Apply theme
apply_theme()

# Authentication gate
if not render_auth_page():
    st.stop()

# Header
st.title(f"💻 {APP_NAME}")
st.caption(APP_CAPTION)

# User info in sidebar
st.sidebar.markdown(f"👤 Logged in as **{st.session_state.username}**")
if st.sidebar.button("🚪 Logout"):
    logout()

st.sidebar.divider()

# Render UI
tool = render_sidebar()
user_input, tone, generate = render_input()

# Handle generation
if generate and user_input:
    progress_bar = render_progress()

    try:
        prompt = build_prompt(tool, user_input, tone)

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}]
        )

        result = response.choices[0].message.content
        st.session_state.generated_result = result
        add_to_history(tool, tone, user_input, result)

    except Exception as e:
        st.error(f"Something went wrong: {e}")
    finally:
        progress_bar.empty()

elif generate and not user_input:
    st.warning("Please enter some input text before generating.")

# Render output
render_output()
