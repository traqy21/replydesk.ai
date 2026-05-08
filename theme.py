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
    /* Light theme — clean, modern, professional */
    .stApp {
        background-color: #F5F5FC !important;
        color: #0F172A !important;
    }
    .block-container {
        background-color: #F5F5FC !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #0F172A !important;
    }
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-color: #E2E8F0 !important;
        border-radius: 8px !important;
    }
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-color: #E2E8F0 !important;
        border-radius: 8px !important;
    }
    .stTextInput input::placeholder {
        color: #94A3B8 !important;
        opacity: 1 !important;
    }
    .stTextArea textarea::placeholder {
        color: #94A3B8 !important;
        opacity: 1 !important;
    }
    .stSelectbox > div > div {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border-color: #E2E8F0 !important;
        border-radius: 8px !important;
    }
    .stButton > button {
        border: 1px solid #E2E8F0 !important;
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
    }
    .stButton > button:hover {
        border-color: #4F46E5 !important;
        background-color: #EEF2FF !important;
        color: #4F46E5 !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #4F46E5 !important;
        color: #FFFFFF !important;
        border-color: #4F46E5 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #4338CA !important;
        border-color: #4338CA !important;
        color: #FFFFFF !important;
    }
    /* Also target active/selected state */
    .stButton > button[kind="primary"] p,
    .stButton > button[kind="primary"] span,
    .stButton > button[kind="primary"] div {
        color: #FFFFFF !important;
    }
    /* Download button */
    .stDownloadButton > button {
        border: 1px solid #E2E8F0 !important;
        color: #0F172A !important;
        background-color: #FFFFFF !important;
        border-radius: 8px !important;
    }
    .stDownloadButton > button:hover {
        border-color: #4F46E5 !important;
        background-color: #EEF2FF !important;
        color: #4F46E5 !important;
    }
    .stMarkdown, p, h1, h2, h3, h4, h5, h6, label {
        color: #0F172A !important;
    }
    .stMetric label {
        color: #64748B !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #0F172A !important;
    }
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #EEF2FF !important;
        border-radius: 8px !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #64748B !important;
    }
    .stTabs [aria-selected="true"] {
        color: #4F46E5 !important;
    }
    div[data-testid="stCodeBlock"] {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
    }
    .stInfo, [data-testid="stInfo"] {
        background-color: #EEF2FF !important;
        border-color: #4F46E5 !important;
    }
    .stSuccess, [data-testid="stSuccess"] {
        background-color: #F0FDF4 !important;
    }
    .stError, [data-testid="stError"] {
        background-color: #FEF2F2 !important;
    }
    .stWarning, [data-testid="stWarning"] {
        background-color: #FFFBEB !important;
    }
    /* Caption / secondary text */
    .stCaption, small, [data-testid="stCaptionContainer"] p {
        color: #0a000f !important;
    }
    /* Divider */
    hr {
        border-color: #E2E8F0 !important;
    }
</style>
"""

RESPONSIVE_CSS = """
<style>
    /* Hide deploy button only — keep header visible for hamburger menu */
    .stDeployButton {
        display: none !important;
    }

    /* Hide "Press Enter to apply" hint on text inputs */
    .stTextInput div[data-testid="InputInstructions"] {
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


def get_logo() -> str:
    """Return the appropriate logo path based on current theme."""
    if st.session_state.get("theme") == "Light":
        return "assets/logo-wide-dark.svg"
    return "assets/logo-wide.svg"


def apply_theme():
    """Apply the selected theme, responsive CSS, and Open Graph meta tags."""
    # Open Graph meta tags for social media link previews
    app_url = __import__('os').getenv("APP_URL", "https://replydesk-ai.com")
    st.markdown(f"""
    <head>
        <meta property="og:title" content="Replydesk AI — Free AI Writing Tools for Professionals" />
        <meta property="og:description" content="Generate client replies, emails, meeting notes, daily reports and more in seconds. Free to try — 10 generations per day, no credit card required." />
        <meta property="og:image" content="https://replydesk-ai.com/og-image.png" />
        <meta property="og:url" content="{app_url}" />
        <meta property="og:type" content="website" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="Replydesk AI — Free AI Writing Tools for Professionals" />
        <meta name="twitter:description" content="Generate client replies, emails, meeting notes, daily reports and more in seconds. Free to try." />
        <meta name="twitter:image" content="https://replydesk-ai.com/og-image.png" />
    </head>
    """, unsafe_allow_html=True)

    # Responsive styles always applied
    st.markdown(RESPONSIVE_CSS, unsafe_allow_html=True)

    # Theme-specific styles
    if st.session_state.get("theme") == "Dark":
        st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
    else:
        st.markdown(LIGHT_THEME_CSS, unsafe_allow_html=True)
