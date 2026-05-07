"""History page — view and manage past generations."""

import streamlit as st


def render():
    """Render the history page."""
    st.markdown("#### 📜 History")
    st.caption("View and manage your past generations")

    if not st.session_state.get("history"):
        st.info("No history yet. Generate some content from the Tools page to see it here.")
        return

    history = st.session_state.history
    st.divider()

    # Filter
    filter_col, _ = st.columns([1, 3])
    with filter_col:
        filter_tool = st.selectbox(
            "Filter by tool",
            ["All"] + sorted(set(e["tool"] for e in history)),
            key="history_filter",
        )

    entries = list(reversed(history))
    if filter_tool != "All":
        entries = [e for e in entries if e["tool"] == filter_tool]

    st.caption(f"Showing {len(entries)} of {len(history)} entries")

    for i, entry in enumerate(entries):
        with st.expander(
            f"**{entry['tool']}** — {entry['timestamp']} ({entry['tone']})",
            expanded=False,
        ):
            st.markdown("**Input:**")
            st.text(entry["input"][:500] + ("..." if len(entry["input"]) > 500 else ""))

            st.markdown("**Output:**")
            st.code(entry["output"], language="markdown")

            col_load, col_export, col_delete = st.columns(3)
            with col_load:
                if st.button("♻️ Load to Editor", key=f"hist_load_{i}", use_container_width=True):
                    st.session_state.generated_result = entry["output"]
                    st.success("Loaded! Switch to Tools page to view.")
            with col_export:
                st.download_button(
                    "⬇️ Export",
                    data=entry["output"],
                    file_name=f"{entry['tool'].lower().replace(' ', '_')}_{entry['timestamp'][:10]}.txt",
                    mime="text/plain",
                    key=f"hist_export_{i}",
                    use_container_width=True,
                )
            with col_delete:
                if st.button("🗑️ Delete", key=f"hist_del_{i}", use_container_width=True):
                    original_index = len(history) - 1 - i
                    st.session_state.history.pop(original_index)
                    st.rerun()

    st.divider()
    if st.button("🗑️ Clear All History", use_container_width=True, type="secondary"):
        st.session_state.history = []
        st.rerun()
