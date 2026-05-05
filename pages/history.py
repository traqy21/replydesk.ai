"""History page — view and manage past generations."""

import streamlit as st


def render():
    """Render the history page."""
    st.markdown("#### 📜 History")
    st.caption("View and manage your past generations")

    if not st.session_state.get("history"):
        st.info("No history yet. Generate some content from the Tools page to see it here.")
        return

    st.divider()

    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Generations", len(st.session_state.history))
    with col2:
        tools_used = set(entry["tool"] for entry in st.session_state.history)
        st.metric("Tools Used", len(tools_used))
    with col3:
        from auth import get_remaining_generations
        st.metric("Remaining Today", get_remaining_generations())

    st.divider()

    # Filter
    filter_tool = st.selectbox(
        "Filter by tool",
        ["All"] + list(set(entry["tool"] for entry in st.session_state.history)),
        key="history_filter",
    )

    # Display history entries
    entries = list(reversed(st.session_state.history))
    if filter_tool != "All":
        entries = [e for e in entries if e["tool"] == filter_tool]

    for i, entry in enumerate(entries):
        with st.expander(f"**{entry['tool']}** — {entry['timestamp']} ({entry['tone']})", expanded=False):
            st.markdown("**Input:**")
            st.text(entry["input"][:500] + ("..." if len(entry["input"]) > 500 else ""))

            st.markdown("**Output:**")
            st.code(entry["output"], language="markdown")

            col_load, col_delete = st.columns(2)
            with col_load:
                if st.button("♻️ Load to Editor", key=f"hist_load_{i}", use_container_width=True):
                    st.session_state.generated_result = entry["output"]
                    st.success("Loaded! Switch to Tools page to view.")

            with col_delete:
                if st.button("🗑️ Delete", key=f"hist_del_{i}", use_container_width=True):
                    # Find and remove from original list
                    original_index = len(st.session_state.history) - 1 - i
                    st.session_state.history.pop(original_index)
                    st.rerun()

    st.divider()

    # Clear all
    if st.button("🗑️ Clear All History", use_container_width=True, type="secondary"):
        st.session_state.history = []
        st.rerun()
