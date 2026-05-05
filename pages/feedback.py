"""Feedback page — collect user feedback and suggestions."""

import streamlit as st
import json
import os
from datetime import datetime

FEEDBACK_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "feedback.json")


def _load_feedback() -> list:
    """Load feedback entries from file."""
    if not os.path.exists(FEEDBACK_FILE):
        return []
    with open(FEEDBACK_FILE, "r") as f:
        return json.load(f)


def _save_feedback(entries: list):
    """Save feedback entries to file."""
    with open(FEEDBACK_FILE, "w") as f:
        json.dump(entries, f, indent=2)


CATEGORIES = [
    "General Feedback",
    "Bug Report",
    "Feature Request",
    "UI/UX Suggestion",
    "Performance Issue",
    "Other",
]

RATINGS = ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]


def render():
    """Render the feedback page."""
    st.markdown("#### 💬 Feedback")
    st.caption("Help us improve Replydesk AI — your input matters")

    st.divider()

    # Feedback form
    category = st.selectbox("Category", CATEGORIES)
    rating = st.select_slider("How would you rate your experience?", options=RATINGS, value="⭐⭐⭐")

    subject = st.text_input("Subject", placeholder="Brief summary of your feedback")
    message = st.text_area("Your Feedback", placeholder="Tell us what's on your mind...", height=150)

    if st.button("📨 Submit Feedback", use_container_width=True):
        if not subject or not message:
            st.error("Please fill in both the subject and feedback message.")
        else:
            entry = {
                "email": st.session_state.get("email", "anonymous"),
                "category": category,
                "rating": rating,
                "subject": subject,
                "message": message,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            entries = _load_feedback()
            entries.append(entry)
            _save_feedback(entries)

            st.success("Thank you! Your feedback has been submitted. ✅")
            st.balloons()

    st.divider()

    # Show user's past feedback
    st.markdown("**Your Previous Feedback**")
    entries = _load_feedback()
    user_entries = [e for e in entries if e.get("email") == st.session_state.get("email")]

    if user_entries:
        for entry in reversed(user_entries):
            with st.expander(f"{entry['category']} — {entry['subject']} ({entry['timestamp']})"):
                st.markdown(f"**Rating:** {entry['rating']}")
                st.markdown(f"**Message:** {entry['message']}")
    else:
        st.caption("You haven't submitted any feedback yet.")
