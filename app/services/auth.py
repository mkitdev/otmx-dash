import streamlit as st

from app.core.mlog import log_app, log_user_event

USERNAME = st.secrets["accounts"]["username"]
PASSWORD = st.secrets["accounts"]["password"]
AUTH_ENABLE = st.secrets.get("authentication", {}).get("enable", True)


def init_auth_state():
    """Initialize authentication state in session_state."""
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False

    if "username" not in st.session_state:
        st.session_state.username = None


def is_auth_enabled() -> bool:
    """Just return whether authentication is enabled from secrets."""
    return AUTH_ENABLE


# =========================
# LOGIN
# =========================
def login(username: str, password: str) -> bool:
    """Authenticate user."""
    if username == USERNAME and password == PASSWORD:
        st.session_state.username = username
        st.session_state.is_authenticated = True

        log_user_event("login_success", user_id=username)
        return True

    st.session_state.username = None
    st.session_state.is_authenticated = False

    log_user_event("login_failed", user_id=username)
    return False


# =========================
# FORCE LOGIN BYPASS (DEV ONLY)
# =========================
def force_login_as_guest():
    """Force login as guest user (for dev/testing purposes)."""
    st.session_state.username = "guest"
    st.session_state.is_authenticated = True

    log_app("Auth bypass enabled — auto login as guest")
    log_user_event("login_bypass", user_id="guest")


# =========================
# LOGOUT
# =========================
def logout():
    """Logout user."""
    user = st.session_state.get("username", "unknown")

    st.session_state.username = None
    st.session_state.is_authenticated = False

    log_user_event("logout", user_id=user)
