"""Feedback page — collect user feedback and suggestions."""

import streamlit as st
from datetime import datetime
from feedback_store import save_feedback, load_user_feedback

CATEGORIES = [
    "General Feedback",
    "Bug Report",
    "Feature Request",
    "UI/UX Suggestion",
    "Performance Issue",
    "Other",
]

RATINGS = ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]


def _reset_form():
    """Bump the form key to force all widgets to re-render empty."""
    st.session_state.feedback_form_key = st.session_state.get("feedback_form_key", 0) + 1


def render():
    """Render the feedback page."""
    st.markdown("#### 💬 Feedback")
    st.caption("Help us improve Replydesk AI — your input matters")

    st.divider()

    # Use a versioned key suffix so incrementing it clears all widgets
    k = st.session_state.get("feedback_form_key", 0)

    category = st.selectbox("Category", CATEGORIES, key=f"fb_category_{k}")
    rating = st.select_slider(
        "How would you rate your experience?",
        options=RATINGS,
        value="⭐⭐⭐",
        key=f"fb_rating_{k}",
    )
    subject = st.text_input(
        "Subject",
        placeholder="Brief summary of your feedback",
        key=f"fb_subject_{k}",
    )
    message = st.text_area(
        "Your Feedback",
        placeholder="Tell us what's on your mind...",
        height=150,
        key=f"fb_message_{k}",
    )

    if st.button("📨 Submit Feedback", use_container_width=True, key=f"fb_submit_{k}"):
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
            try:
                save_feedback(entry)
                _reset_form()
                st.success("Thank you! Your feedback has been submitted. ✅")
                st.balloons()
            except Exception as e:
                st.error(f"Could not save feedback: {e}")

    st.divider()

    # Show user's past feedback
    st.markdown("**Your Previous Feedback**")
    try:
        user_entries = load_user_feedback(st.session_state.get("email", ""))
    except Exception as e:
        st.warning(f"Could not load feedback history: {e}")
        user_entries = []

    if user_entries:
        for entry in reversed(user_entries):
            with st.expander(f"{entry['category']} — {entry['subject']} ({entry['timestamp']})"):
                st.markdown(f"**Rating:** {entry['rating']}")
                st.markdown(f"**Message:** {entry['message']}")
    else:
        st.caption("You haven't submitted any feedback yet.")
