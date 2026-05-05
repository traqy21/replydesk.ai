"""Replydesk AI — main application entry point."""

import streamlit as st

from config import APP_NAME, APP_CAPTION, MODEL, client
from prompts import build_prompt
from ui import init_session_state, render_sidebar, render_input, render_output

# Page config
st.set_page_config(page_title=APP_NAME, layout="wide")
st.title(f"💻 {APP_NAME}")
st.caption(APP_CAPTION)

# Initialize state
init_session_state()

# Render UI
tool = render_sidebar()
user_input, tone, generate = render_input()

# Handle generation
if generate and user_input:
    with st.spinner("Generating..."):
        try:
            prompt = build_prompt(tool, user_input, tone)

            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}]
            )

            st.session_state.generated_result = response.choices[0].message.content

        except Exception as e:
            st.error(f"Something went wrong: {e}")

elif generate and not user_input:
    st.warning("Please enter some input text before generating.")

# Render output
render_output()
