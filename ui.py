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


def render_sidebar():
    """Render the sidebar with tool selector, theme toggle, and history."""
    tool = st.sidebar.selectbox("Select Tool", TOOLS)

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

    # History log
    st.sidebar.subheader("📜 History")
    if st.session_state.history:
        for i, entry in enumerate(reversed(st.session_state.history)):
            with st.sidebar.expander(
                f"{entry['tool']} — {entry['timestamp']}", expanded=False
            ):
                st.markdown(f"**Tone:** {entry['tone']}")
                st.markdown(f"**Input:** {entry['input'][:100]}{'...' if len(entry['input']) > 100 else ''}")
                st.code(entry["output"][:300] + ("..." if len(entry["output"]) > 300 else ""), language="markdown")
                if st.button("♻️ Load", key=f"load_{i}"):
                    st.session_state.generated_result = entry["output"]
                    st.rerun()

        if st.sidebar.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()
    else:
        st.sidebar.caption("No history yet.")

    return tool


def render_input():
    """Render the input section. Returns (user_input, tone, generate_clicked)."""
    st.subheader("Input")
    user_input = st.text_area("Paste client message or notes here")
    tone = st.selectbox("Tone", TONES)
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
        # Editable output
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
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    })
