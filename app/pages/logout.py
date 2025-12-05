"""Logout page."""

import streamlit as st

from app.core.mlog import log_user_event
from app.services.auth_guard import get_current_user, require_login

# ============================================================================
# GUARD - REQUIRE LOGIN
# ============================================================================
require_login()


# ============================================================================
# CALLBACK - LOGOUT
# ============================================================================
def on_logout():
    """Callback: Clear auth state."""
    user = st.session_state.get("auth_username", "unknown")
    log_user_event("logout", user_id=user)

    st.session_state.auth_is_authenticated = False
    st.session_state.auth_username = None
    st.session_state.auth_user_role = None

    st.success("✅ Berhasil logout")
    st.rerun()


# ============================================================================
# UI
# ============================================================================
st.title("Logout")

st.write(f"Login sebagai: **{get_current_user()}**")

if st.button("Logout", type="primary", use_container_width=True):
    on_logout()
