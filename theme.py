"""Theme management — dark/light mode and responsive styles."""

import streamlit as st

DARK_THEME_CSS = """
<style>
    /* Dark theme overrides */
    .stApp {
        background-color: #1a1a2e;
        color: #e0e0e0;
    }
    .stTextArea textarea {
        background-color: #16213e;
        color: #e0e0e0;
        border-color: #0f3460;
    }
    .stSelectbox > div > div {
        background-color: #16213e;
        color: #e0e0e0;
    }
    .stButton > button {
        background-color: #0f3460;
        color: #e0e0e0;
        border: 1px solid #533483;
    }
    .stButton > button:hover {
        background-color: #533483;
        border-color: #533483;
    }
    section[data-testid="stSidebar"] {
        background-color: #16213e;
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: #e0e0e0;
    }
</style>
"""

LIGHT_THEME_CSS = """
<style>
    /* Light theme — mostly Streamlit defaults with minor tweaks */
    .stButton > button {
        border: 1px solid #ddd;
    }
    .stButton > button:hover {
        border-color: #4F8EF7;
    }
</style>
"""

RESPONSIVE_CSS = """
<style>
    /* Hide deploy button only — keep header visible for hamburger menu */
    .stDeployButton {
        display: none !important;
    }

    /* ── Hamburger button — make it prominent and easy to tap ── */
    button[data-testid="collapsedControl"] {
        background-color: #4F8EF7 !important;
        border-radius: 50% !important;
        width: 44px !important;
        height: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 2px 8px rgba(79, 142, 247, 0.5) !important;
        border: none !important;
        top: 0.6rem !important;
        left: 0.6rem !important;
    }

    button[data-testid="collapsedControl"]:hover {
        background-color: #3a7de0 !important;
        box-shadow: 0 4px 12px rgba(79, 142, 247, 0.7) !important;
        transform: scale(1.05) !important;
    }

    button[data-testid="collapsedControl"] svg {
        fill: white !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* Responsive layout improvements */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        section[data-testid="stSidebar"] {
            min-width: 240px !important;
            max-width: 75vw !important;
        }
        .stTextArea textarea {
            font-size: 14px;
        }
        h1 {
            font-size: 1.5rem !important;
        }
    }

    @media (max-width: 480px) {
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }
        h1 {
            font-size: 1.2rem !important;
        }
    }
</style>
"""


def apply_theme():
    """Apply the selected theme and responsive CSS."""
    # Responsive styles always applied
    st.markdown(RESPONSIVE_CSS, unsafe_allow_html=True)

    # Theme-specific styles
    if st.session_state.get("theme") == "Dark":
        st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
    else:
        st.markdown(LIGHT_THEME_CSS, unsafe_allow_html=True)
