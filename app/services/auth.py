import streamlit as st

from app.core.mlog import log_app, log_user_event

USERNAME = st.secrets["accounts"]["username"]
PASSWORD = st.secrets["accounts"]["password"]
ROLE = st.secrets["accounts"]["role"]
AUTH_ENABLE = st.secrets.get("authentication", {}).get("enable", True)


def init_auth_state():
    """Initialize authentication state in session_state."""
    if "auth_is_authenticated" not in st.session_state:
        st.session_state.auth_is_authenticated = False

    if "auth_username" not in st.session_state:
        st.session_state.auth_username = None

    if "auth_user_role" not in st.session_state:
        st.session_state.auth_user_role = None


def _is_auth_enabled() -> bool:
    """Check if authentication is enabled from secrets."""
    return AUTH_ENABLE


def _dev_force_login_as_guest():
    """Force login as guest user (development only)."""
    st.session_state.auth_username = "guest"
    st.session_state.auth_is_authenticated = True
    st.session_state.auth_user_role = "guest"

    log_app("Auth disabled via config — auto login as guest")
    log_user_event("login_bypass", user_id="guest")


def _dev_force_login_with_secrets():
    """Force login with credentials from secrets (auth disabled for dev)."""
    st.session_state.auth_username = USERNAME
    st.session_state.auth_is_authenticated = True
    st.session_state.auth_user_role = ROLE

    log_app("Auth disabled via config — auto login with secrets")
    log_user_event("login_bypass", user_id=USERNAME)


def get_current_user() -> str | None:
    """Get the current authenticated user's username."""
    if st.session_state.get("auth_is_authenticated", False):
        return st.session_state.get("auth_username")
    return None


def get_current_user_role() -> str | None:
    """Get the current authenticated user's role."""
    if st.session_state.get("auth_is_authenticated", False):
        return st.session_state.get("auth_user_role")
    return None


def login(username: str, password: str) -> bool:
    """Authenticate user with given username and password."""
    if not _is_auth_enabled():
        # When auth is disabled, use credentials from secrets (bypass login form)
        _dev_force_login_with_secrets()
        return True

    if username == USERNAME and password == PASSWORD:
        st.session_state.auth_username = username
        st.session_state.auth_is_authenticated = True
        st.session_state.auth_user_role = ROLE

        log_user_event("login_success", user_id=username)
        return True

    st.session_state.auth_username = None
    st.session_state.auth_is_authenticated = False
    st.session_state.auth_user_role = None

    log_user_event("login_failed", user_id=username)
    return False


def logout():
    """Logout the current user."""
    user = st.session_state.get("auth_username", "unknown")

    st.session_state.auth_username = None
    st.session_state.auth_is_authenticated = False
    st.session_state.auth_user_role = None

    log_user_event("logout", user_id=user)


# used in pages that require login
def require_login():
    """Require the user to be logged in."""
    if not st.session_state.get("auth_is_authenticated", False):
        st.warning("Silakan login terlebih dahulu.")
        st.stop()


def require_role(required_role: str):
    """Require the user to have a specific role."""
    role = st.session_state.get("auth_user_role")

    if not role:
        st.error("Role tidak ditemukan.")
        st.stop()

    # administrator selalu boleh masuk
    if role not in [required_role, "administrator"]:
        st.error("Anda tidak memiliki akses ke halaman ini.")
        st.stop()
