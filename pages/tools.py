"""Tools page — main generation interface."""

import streamlit as st

from config import MODEL, client
from prompts import build_prompt
from auth import check_rate_limit, increment_generation_count
from ui import render_progress, add_to_history
from logger import get_logger

log = get_logger("tools")

TOOLS = {
    "Client Reply":    {"icon": "💬", "desc": "Craft a professional response to a client message."},
    "Email Generator": {"icon": "📧", "desc": "Draft a structured email from your notes or brief."},
    "Task Summary":    {"icon": "📋", "desc": "Condense your notes into clear, actionable bullet points."},
    "Daily Report":    {"icon": "📊", "desc": "Generate a formatted end-of-day status report."},
}

TONES = ["Friendly", "Formal", "Professional", "Casual"]

TONE_ICONS = {
    "Friendly": "😊",
    "Formal": "🎩",
    "Professional": "💼",
    "Casual": "👋",
}


def render():
    """Render the tools page."""

    # ── Page header ────────────────────────────────────────────────────────
    st.markdown("#### 🛠️ Tools")
    st.caption("Select a tool, write your input, and generate professional content instantly.")
    st.divider()

    # ── Tool selector cards ────────────────────────────────────────────────
    tool_names = list(TOOLS.keys())
    if "selected_tool" not in st.session_state:
        st.session_state.selected_tool = tool_names[0]

    cols = st.columns(len(tool_names))
    for col, name in zip(cols, tool_names):
        info = TOOLS[name]
        is_active = st.session_state.selected_tool == name
        with col:
            if st.button(
                f"{info['icon']} {name}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
                key=f"tool_btn_{name}",
            ):
                st.session_state.selected_tool = name
                st.session_state.generated_result = ""
                st.rerun()

    tool = st.session_state.selected_tool
    st.caption(f"_{TOOLS[tool]['desc']}_")

    st.write("")

    # ── Two-column layout: Input | Output ──────────────────────────────────
    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("**✏️ Input**")

        user_input = st.text_area(
            "Your message or notes",
            placeholder=_get_placeholder(tool),
            height=260,
            label_visibility="collapsed",
            key="tool_input",
        )

        tone_col, btn_col = st.columns([1, 2], gap="small")
        with tone_col:
            tone = st.selectbox(
                "Tone",
                TONES,
                format_func=lambda t: f"{TONE_ICONS[t]} {t}",
                key="tool_tone",
                label_visibility="collapsed",
            )
        with btn_col:
            generate = st.button(
                "✨ Generate",
                use_container_width=True,
                type="primary",
                key="generate_btn",
            )

        # Clear output when tone changes
        if st.session_state.get("last_tone") and st.session_state.last_tone != tone:
            st.session_state.generated_result = ""
        st.session_state.last_tone = tone

    with right:
        st.markdown("**📄 Output**")

        # ── Handle generation ──────────────────────────────────────────────
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

        # ── Output display ─────────────────────────────────────────────────
        if st.session_state.get("generated_result"):
            edited = st.text_area(
                "Result",
                value=st.session_state.generated_result,
                height=260,
                key="output_editor",
                label_visibility="collapsed",
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("💾 Save", use_container_width=True, key="save_btn"):
                    st.session_state.generated_result = edited
                    st.success("Saved!")
            with c2:
                if st.button("📋 Copy", use_container_width=True, key="copy_btn"):
                    st.code(st.session_state.generated_result, language="markdown")
            with c3:
                if st.button("🗑️ Clear", use_container_width=True, key="clear_btn"):
                    st.session_state.generated_result = ""
                    st.rerun()
        else:
            st.markdown(
                """
                <div style="
                    height: 260px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    border: 1.5px dashed #444;
                    border-radius: 8px;
                    color: #888;
                    font-size: 14px;
                    gap: 8px;
                ">
                    <span style="font-size: 32px;">✨</span>
                    <span>Your generated content will appear here</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _get_placeholder(tool: str) -> str:
    """Return a contextual placeholder for the input area."""
    placeholders = {
        "Client Reply": "Paste the client's message here...\n\nE.g. Hi, I wanted to follow up on the project status...",
        "Email Generator": "Describe what the email should cover...\n\nE.g. Send a follow-up to John about the proposal we sent last week.",
        "Task Summary": "Paste your raw notes or task list here...\n\nE.g. - Called client\n- Updated spreadsheet\n- Reviewed draft",
        "Daily Report": "List your tasks and updates for today...\n\nE.g. Completed onboarding doc, reviewed 3 tickets, pending: client call tomorrow.",
    }
    return placeholders.get(tool, "Enter your text here...")
