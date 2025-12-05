"""ini sample landing page. default ketika user berhasil login."""

import streamlit as st

from app.core.mlog import log_user_activity

# Track when user opens this page
log_user_activity(
    "page_load",
    user_id=st.session_state.get("auth_username", "guest"),
    page="Landing",
)

st.write("Selamat datang di Otomax Dash!")
