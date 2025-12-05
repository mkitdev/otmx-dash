"""Authentication guard functions & helpers for UI layer.

These functions manage session state and provide guards for pages.
"""

import streamlit as st

from app.core.mlog import log_app


def init_auth_state():
    """Initialize authentication state in session_state (UI responsibility).

    Should be called early in pages that use auth.
    """
    if "auth_is_authenticated" not in st.session_state:
        st.session_state.auth_is_authenticated = False

    if "auth_username" not in st.session_state:
        st.session_state.auth_username = None

    if "auth_user_role" not in st.session_state:
        st.session_state.auth_user_role = None

    if "auth_enabled" not in st.session_state:
        auth_config = st.secrets.get("authentication", {})
        auth_enabled = auth_config.get("enable", True)
        st.session_state.auth_enabled = auth_enabled
        log_app(f"Auth system initialized: enabled={auth_enabled}")


def is_auth_enabled() -> bool:
    """Check if authentication is enabled from secrets."""
    return st.session_state.get("auth_enabled", True)


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


def require_login():
    """Guard: Require user to be authenticated.

    Raises:
        StreamlitAPIException (via st.stop) if not authenticated
    """
    init_auth_state()

    if not st.session_state.get("auth_is_authenticated", False):
        st.warning("⚠️ Silakan login terlebih dahulu.")
        st.stop()


def require_role(required_role: str):
    """Guard: Require user to have specific role.

    Args:
        required_role: Required role name

    Note:
        Users with "administrator" role always pass this guard.

    Raises:
        StreamlitAPIException (via st.stop) if role check fails
    """
    init_auth_state()
    require_login()

    role = st.session_state.get("auth_user_role")

    if not role:
        st.error("❌ Role tidak ditemukan.")
        st.stop()

    # administrator always allowed
    if role not in [required_role, "administrator"]:
        st.error(f"❌ Akses ditolak. Role '{required_role}' diperlukan.")
        st.stop()
