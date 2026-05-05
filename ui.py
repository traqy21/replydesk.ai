"""UI components for the Streamlit app."""

import streamlit as st

# Available tools and tones
TOOLS = ["Client Reply", "Email Generator", "Task Summary", "Daily Report"]
TONES = ["Friendly", "Formal", "Professional", "Casual"]


def init_session_state():
    """Initialize session state for persisting output."""
    if "generated_result" not in st.session_state:
        st.session_state.generated_result = ""


def render_sidebar():
    """Render the sidebar tool selector. Returns the selected tool."""
    return st.sidebar.selectbox("Select Tool", TOOLS)


def render_input():
    """Render the input section. Returns (user_input, tone, generate_clicked)."""
    st.subheader("Input")
    user_input = st.text_area("Paste client message or notes here")
    tone = st.selectbox("Tone", TONES)
    generate = st.button("✨ Generate")
    return user_input, tone, generate


def render_output():
    """Render the output section with persisted results."""
    st.subheader("Output")

    if st.session_state.generated_result:
        st.code(st.session_state.generated_result, language="markdown")

        if st.button("🗑️ Clear"):
            st.session_state.generated_result = ""
            st.rerun()
    else:
        st.info("Enter input and click Generate.")
