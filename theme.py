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
        border-color: #ff4b4b;
    }
</style>
"""

RESPONSIVE_CSS = """
<style>
    /* Hide Streamlit deploy button and toolbar */
    .stDeployButton,
    [data-testid="stToolbar"],
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* Responsive layout improvements */
    @media (max-width: 768px) {
        .stApp > header {
            padding: 0.5rem;
        }
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        section[data-testid="stSidebar"] {
            min-width: 200px !important;
            max-width: 250px !important;
        }
        .stTextArea textarea {
            font-size: 14px;
        }
        h1 {
            font-size: 1.5rem !important;
        }
    }

    @media (max-width: 480px) {
        section[data-testid="stSidebar"] {
            min-width: 180px !important;
        }
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
