import streamlit as st

from app.core.mlog import log_app, log_user_event

USERS = st.secrets.get("users", {})
AUTH_ENABLE = st.secrets.get("authentication", {}).get("enable", True)

# Default user jika auth disabled (untuk development)
DEFAULT_USER = "admin"
# [ ] TODO: Fallback config ketika file secrets kosong atau tidak ada


def init_auth_state():
    """Initialize authentication state in session_state."""
    if "auth_is_authenticated" not in st.session_state:
        st.session_state.auth_is_authenticated = False

    if "auth_username" not in st.session_state:
        st.session_state.auth_username = None

    if "auth_user_role" not in st.session_state:
        st.session_state.auth_user_role = None

    # Track auth setup only once
    if "auth_enabled" not in st.session_state:
        log_app(f"Auth system initialized: enabled={AUTH_ENABLE}")
        st.session_state.auth_enabled = AUTH_ENABLE


def _is_auth_enabled() -> bool:
    """Check if authentication is enabled from secrets."""
    return st.session_state.get("auth_enabled", AUTH_ENABLE)


def _dev_auto_login():
    """Auto-login with default user when auth is disabled (development only)."""
    user_data = USERS.get(DEFAULT_USER, {})
    st.session_state.auth_username = user_data.get("username", DEFAULT_USER)
    st.session_state.auth_is_authenticated = True
    st.session_state.auth_user_role = user_data.get("role", "user")

    log_app(f"Auth disabled — auto login as {DEFAULT_USER}")
    log_user_event("login_bypass", user_id=DEFAULT_USER)


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
    """Authenticate user with given username and password.

    If auth is disabled: auto-login as default user (for development).
    If auth is enabled: validate credentials against users in secrets.
    """
    # When auth is disabled, auto-login as default user
    if not _is_auth_enabled():
        _dev_auto_login()
        return True

    # When auth is enabled, validate credentials from users in secrets
    for user_data in USERS.values():
        if username == user_data.get("username") and password == user_data.get(
            "password"
        ):
            st.session_state.auth_username = username
            st.session_state.auth_is_authenticated = True
            st.session_state.auth_user_role = user_data.get("role", "user")

            log_user_event("login_success", user_id=username)
            return True

    # Login failed
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
