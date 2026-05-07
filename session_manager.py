"""Session persistence using server-side session store + URL session ID.

How it works:
1. On login, generate a session ID and store user data in a server-side
   cache (st.cache_resource — persists across reruns for all users).
2. Store the session ID in st.query_params so it survives page refresh.
3. On each page load, read the session ID from query params and restore
   the user's session from the server-side cache.

This approach requires no cookies, no localStorage, no extra libraries.
The session ID stays in the URL (e.g. ?sid=abc123) and is invisible to
the user since it's just a query parameter.
"""

import secrets
import time
import os

import streamlit as st
from logger import get_logger

log = get_logger("session")

SESSION_EXPIRY_SECONDS = 7 * 24 * 3600  # 7 days


@st.cache_resource
def _session_store() -> dict:
    """Server-side session store shared across all users and reruns."""
    return {}


def save_session(email: str) -> str:
    """Create a new session, store it server-side, and set the session ID
    in query params so it persists on refresh.
    Returns the session ID.
    """
    sid = secrets.token_urlsafe(32)
    _session_store()[sid] = {
        "email": email,
        "created_at": time.time(),
        "expires_at": time.time() + SESSION_EXPIRY_SECONDS,
    }
    st.query_params["sid"] = sid
    log.info("session_saved", extra={"email": email, "sid": sid[:8]})
    return sid


def load_session() -> str | None:
    """Read session ID from query params and return email if valid."""
    sid = st.query_params.get("sid", "")
    if not sid:
        return None

    store = _session_store()
    session = store.get(sid)
    if not session:
        return None

    # Check expiry
    if time.time() > session.get("expires_at", 0):
        del store[sid]
        log.info("session_expired", extra={"sid": sid[:8]})
        return None

    return session.get("email")


def clear_session():
    """Remove the session from the server-side store and clear query params."""
    sid = st.query_params.get("sid", "")
    if sid:
        _session_store().pop(sid, None)
        st.query_params.pop("sid", None)
    log.info("session_cleared")


# No-ops for backward compat
def init_cookie_controller():
    pass


def inject_session_reader():
    pass


def load_session_from_query() -> str | None:
    return None
