"""sample page produk."""

import streamlit as st

from app.core.mlog import log_user_activity

# Track when user opens this page
log_user_activity(
    "page_load",
    user_id=st.session_state.get("auth_username", "guest"),
    page="Produk",
)

st.write("Ini adalah halaman Produk")
