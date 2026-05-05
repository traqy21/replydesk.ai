"""UI components for the Streamlit app."""

import streamlit as st
from datetime import datetime

# Available tools and tones
TOOLS = ["Client Reply", "Email Generator", "Task Summary", "Daily Report"]
TONES = ["Friendly", "Formal", "Professional", "Casual"]


def init_session_state():
    """Initialize session state for persisting output and history."""
    if "generated_result" not in st.session_state:
        st.session_state.generated_result = ""
    if "history" not in st.session_state:
        st.session_state.history = []
    if "theme" not in st.session_state:
        st.session_state.theme = "Light"
    if "last_tone" not in st.session_state:
        st.session_state.last_tone = ""


def render_input():
    """Render the input section. Returns (user_input, tone, generate_clicked)."""
    st.subheader("Input")
    user_input = st.text_area("Paste client message or notes here")
    tone = st.selectbox("Tone", TONES)

    # Clear output when tone changes
    if st.session_state.get("last_tone") and st.session_state.last_tone != tone:
        st.session_state.generated_result = ""
    st.session_state.last_tone = tone

    generate = st.button("✨ Generate", use_container_width=True)
    return user_input, tone, generate


def render_progress():
    """Render a progress bar to simulate loading."""
    import time

    progress_bar = st.progress(0, text="Generating your content...")
    for percent in range(0, 101, 20):
        time.sleep(0.1)
        progress_bar.progress(percent, text="Generating your content...")
    return progress_bar


def render_output():
    """Render the output section with editable results."""
    st.subheader("Output")

    if st.session_state.generated_result:
        edited = st.text_area(
            "Generated Result (editable)",
            value=st.session_state.generated_result,
            height=300,
            key="output_editor",
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("💾 Save Edits", use_container_width=True):
                st.session_state.generated_result = edited
                st.success("Edits saved!")

        with col2:
            if st.button("📋 Copy to Clipboard", use_container_width=True):
                st.code(st.session_state.generated_result, language="markdown")

        with col3:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.generated_result = ""
                st.rerun()
    else:
        st.info("Enter input and click Generate.")


def add_to_history(tool: str, tone: str, user_input: str, output: str):
    """Add a generation result to the history log."""
    st.session_state.history.append({
        "tool": tool,
        "tone": tone,
        "input": user_input,
        "output": output,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
