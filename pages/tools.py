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
    "Meeting Notes":   {"icon": "🗒️", "desc": "Turn raw meeting notes into a structured summary with action items."},
    "Follow-up Email": {"icon": "↩️", "desc": "Write a professional follow-up based on a previous conversation."},
    "Tone Rewriter":          {"icon": "✏️", "desc": "Rewrite any message in a different tone while keeping the same meaning."},
    "Subject Line Generator": {"icon": "📌", "desc": "Generate 5 compelling subject line options for any email."},
    "Message Shortener":      {"icon": "✂️", "desc": "Shorten any message while keeping all the key information."},
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

        if user_input:
            st.caption(f"📝 {len(user_input.split())} words · {len(user_input)} characters")

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
                    # Bump output key version to force widget re-render with new content
                    st.session_state.output_version = st.session_state.get("output_version", 0) + 1
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
            ov = st.session_state.get("output_version", 0)
            edited = st.text_area(
                "Result",
                value=st.session_state.generated_result,
                height=260,
                key=f"output_editor_{ov}",
                label_visibility="collapsed",
            )

            # Word / character count
            word_count = len(edited.split())
            char_count = len(edited)
            st.caption(f"📝 {word_count} words · {char_count} characters")

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("💾 Save", use_container_width=True, key="save_btn"):
                    st.session_state.generated_result = edited
                    st.success("Saved!")
            with c2:
                # Real clipboard copy via JS
                _copy_to_clipboard(edited, key=f"copy_{ov}")
            with c3:
                st.download_button(
                    "⬇️ Export",
                    data=edited,
                    file_name=f"{tool.lower().replace(' ', '_')}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key=f"export_btn_{ov}",
                )
            with c4:
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


def _copy_to_clipboard(text: str, key: str = "copy"):
    """Render a real copy-to-clipboard button using JS navigator.clipboard API."""
    import streamlit.components.v1 as components
    escaped = text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    components.html(
        f"""
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ margin: 0; padding: 0; background: transparent; }}
            .copy-btn {{
                width: 100%;
                height: 38px;
                padding: 0 0.75rem;
                font-size: 0.875rem;
                font-family: "Source Sans Pro", sans-serif;
                font-weight: 400;
                border-radius: 0.5rem;
                border: 1px solid rgba(250,250,250,0.2);
                background-color: #0f3460;
                color: #e0e0e0;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 6px;
                transition: background-color 0.2s, border-color 0.2s;
            }}
            .copy-btn:hover {{
                background-color: #533483;
                border-color: #533483;
            }}
            .copy-btn.success {{
                background-color: #16a34a !important;
                border-color: #16a34a !important;
                color: white !important;
            }}
        </style>
        <button class="copy-btn" id="copyBtn" onclick="
            navigator.clipboard.writeText(`{escaped}`)
                .then(() => {{
                    const btn = document.getElementById('copyBtn');
                    btn.classList.add('success');
                    btn.innerHTML = '✅ Copied!';
                    setTimeout(() => {{
                        btn.classList.remove('success');
                        btn.innerHTML = '📋 Copy';
                    }}, 2000);
                }})
                .catch(() => {{
                    const btn = document.getElementById('copyBtn');
                    btn.innerHTML = '❌ Failed';
                    setTimeout(() => {{ btn.innerHTML = '📋 Copy'; }}, 2000);
                }});
        ">📋 Copy</button>
        """,
        height=46,
    )


def _get_placeholder(tool: str) -> str:
    """Return a contextual placeholder for the input area."""
    placeholders = {
        "Client Reply": "Paste the client's message here...\n\nE.g. Hi, I wanted to follow up on the project status...",
        "Email Generator": "Describe what the email should cover...\n\nE.g. Send a follow-up to John about the proposal we sent last week.",
        "Task Summary": "Paste your raw notes or task list here...\n\nE.g. - Called client\n- Updated spreadsheet\n- Reviewed draft",
        "Daily Report": "List your tasks and updates for today...\n\nE.g. Completed onboarding doc, reviewed 3 tickets, pending: client call tomorrow.",
        "Meeting Notes": "Paste your raw meeting notes here...\n\nE.g. Discussed Q2 targets. John to send report by Friday. Budget approved for new hire.",
        "Follow-up Email": "Describe the context of the previous interaction...\n\nE.g. Sent a proposal to Sarah last week about the website redesign project. No response yet.",
        "Tone Rewriter": "Paste the message you want to rewrite...\n\nE.g. Hey, just checking if you got my last email. Need an answer ASAP.",
        "Subject Line Generator": "Paste your email body or describe what the email is about...\n\nE.g. Following up on the proposal I sent last week about the website redesign project.",
        "Message Shortener": "Paste the message you want to shorten...\n\nE.g. I wanted to reach out to you today to follow up on the conversation we had last Tuesday regarding the upcoming project timeline and whether or not the deliverables we discussed are still on track...",
    }
    return placeholders.get(tool, "Enter your text here...")
