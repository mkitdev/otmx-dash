"""Logout page."""

import streamlit as st

from app.core.mlog import log_user_event
from app.services.auth import get_auth, get_current_user, require_login, save_auth

# ============================================================================
# GUARD - REQUIRE LOGIN
# ============================================================================
require_login()


# ============================================================================
# CALLBACK - LOGOUT
# ============================================================================
def on_logout():
    """Callback: Clear auth state."""
    user = get_current_user() or "unknown"
    log_user_event("logout", user_id=user)

    auth = get_auth()
    auth.logout()
    save_auth(auth)

    st.success("✅ Berhasil logout")
    st.rerun()


# ============================================================================
# UI
# ============================================================================
st.title("Logout")

st.write(f"Login sebagai: **{get_current_user()}**")

if st.button("Logout", type="primary", use_container_width=True):
    on_logout()
