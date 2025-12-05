"""Authentication guards - access control for pages."""

import streamlit as st

from app.services.auth.adapter import get_auth


def require_login() -> None:
    """Guard: Require user to be authenticated.

    Halts page execution if not authenticated.

    Raises:
        StreamlitAPIException (via st.stop) if not authenticated
    """
    auth = get_auth()

    if not auth.is_authenticated:
        st.warning("⚠️ Silakan login terlebih dahulu.")
        st.stop()


def require_role(required_role: str) -> None:
    """Guard: Require user to have specific role.

    Admin always passes this check.
    Halts page execution if role check fails.

    Args:
        required_role: Required role to access page

    Raises:
        StreamlitAPIException (via st.stop) if role check fails
    """
    require_login()

    auth = get_auth()

    if not auth.can_access(required_role):
        st.error(f"❌ Akses ditolak. Role '{required_role}' diperlukan.")
        st.stop()
