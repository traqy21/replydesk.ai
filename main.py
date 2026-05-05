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
from auth import render_auth_page, logout, check_rate_limit, increment_generation_count, get_remaining_generations

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
st.markdown("### ✉️ Replydesk AI")
st.caption(APP_CAPTION)

# User info in sidebar
st.sidebar.markdown(f"👤 **{st.session_state.email}**")
st.sidebar.caption(f"📋 {st.session_state.job_position}")
st.sidebar.caption(f"⚡ {get_remaining_generations()} generations remaining today")
if st.sidebar.button("🚪 Logout"):
    logout()

st.sidebar.divider()

# Render UI
tool = render_sidebar()

# Display selected tool in main content
TOOL_DESCRIPTIONS = {
    "Client Reply": "Craft a professional response to a client message.",
    "Email Generator": "Draft a structured email from your notes or brief.",
    "Task Summary": "Condense your notes into clear, actionable bullet points.",
    "Daily Report": "Generate a formatted end-of-day status report.",
}
st.markdown(f"#### 🛠️ {tool}")
st.caption(TOOL_DESCRIPTIONS.get(tool, ""))

user_input, tone, generate = render_input()

# Handle generation
if generate and user_input:
    # Check rate limit
    allowed, limit_message = check_rate_limit()
    if not allowed:
        st.error(limit_message)
    else:
        progress_bar = render_progress()

        try:
            prompt = build_prompt(tool, user_input, tone, st.session_state.job_position)

            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}]
            )

            result = response.choices[0].message.content
            st.session_state.generated_result = result
            add_to_history(tool, tone, user_input, result)
            increment_generation_count()

        except Exception as e:
            st.error(f"Something went wrong: {e}")
        finally:
            progress_bar.empty()

elif generate and not user_input:
    st.warning("Please enter some input text before generating.")

# Render output
render_output()
