"""Dashboard page — usage stats and activity overview."""

from collections import Counter
from datetime import datetime

import streamlit as st
from auth import get_remaining_generations, MAX_GENERATIONS_PER_DAY


def render():
    """Render the usage dashboard page."""
    st.markdown("#### 📊 Dashboard")
    st.caption("Your usage stats and activity overview")
    st.divider()

    history = st.session_state.get("history", [])
    today = datetime.now().strftime("%Y-%m-%d")
    remaining = get_remaining_generations()
    used_today = MAX_GENERATIONS_PER_DAY - remaining
    today_entries = [e for e in history if e["timestamp"].startswith(today)]

    # ── Key metrics ────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Generations", st.session_state.get("total_generations", 0))
    c2.metric("Generated Today", used_today)
    c3.metric("Remaining Today", remaining)
    c4.metric("Daily Limit", MAX_GENERATIONS_PER_DAY)

    # Daily usage progress bar
    st.write("")
    progress = used_today / MAX_GENERATIONS_PER_DAY
    st.caption(f"Daily usage: {used_today} / {MAX_GENERATIONS_PER_DAY}")
    st.progress(progress)

    st.divider()

    if not history:
        st.info("No generations yet. Head to the Tools page to get started.")
        return

    # ── Charts ─────────────────────────────────────────────────────────────
    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("**Generations by Tool**")
        tool_counts = Counter(e["tool"] for e in history)
        st.bar_chart(dict(tool_counts))

    with right:
        st.markdown("**Generations by Tone**")
        tone_counts = Counter(e["tone"] for e in history)
        st.bar_chart(dict(tone_counts))

    st.divider()

    # ── Most used tool ─────────────────────────────────────────────────────
    if history:
        most_used = tool_counts.most_common(1)[0]
        st.markdown("**Insights**")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"🏆 Most used tool: **{most_used[0]}** ({most_used[1]} times)")
        with col2:
            tools_tried = len(set(e["tool"] for e in history))
            total_tools = 7
            st.info(f"🛠️ Tools explored: **{tools_tried} of {total_tools}**")
