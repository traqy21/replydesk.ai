"""Tools page — main generation interface."""

import streamlit as st

from config import MODEL, client
from prompts import build_prompt
from auth import check_rate_limit, increment_generation_count
from ui import render_input, render_output, render_progress, add_to_history
from logger import get_logger

log = get_logger("tools")

TOOL_DESCRIPTIONS = {
    "Client Reply": "Craft a professional response to a client message.",
    "Email Generator": "Draft a structured email from your notes or brief.",
    "Task Summary": "Condense your notes into clear, actionable bullet points.",
    "Daily Report": "Generate a formatted end-of-day status report.",
}

TOOLS = ["Client Reply", "Email Generator", "Task Summary", "Daily Report"]


def render():
    """Render the tools page."""
    st.markdown("#### 🛠️ Tools")
    st.caption("Select a tool and generate professional content")

    # Tool selector
    tool = st.selectbox("Select Tool", TOOLS)
    st.caption(TOOL_DESCRIPTIONS.get(tool, ""))

    st.divider()

    # Input and generation
    user_input, tone, generate = render_input()

    # Handle generation
    if generate and user_input:
        allowed, limit_message = check_rate_limit()
        if not allowed:
            log.warning("rate_limit_hit", extra={
                "email": st.session_state.get("email"),
                "tool": tool,
            })
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
                log.info("generation_success", extra={
                    "email": st.session_state.get("email"),
                    "tool": tool,
                    "tone": tone,
                    "model": MODEL,
                })

            except Exception as e:
                log.error("generation_failed", extra={
                    "email": st.session_state.get("email"),
                    "tool": tool,
                    "error": str(e),
                }, exc_info=True)
                st.error(f"Something went wrong: {e}")
            finally:
                progress_bar.empty()

    elif generate and not user_input:
        st.warning("Please enter some input text before generating.")

    # Output
    render_output()
