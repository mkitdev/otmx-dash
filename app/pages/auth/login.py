"""Login page with state management."""

import streamlit as st

from app.services.auth import (
    AuthConfig,
    get_auth,
    get_default_user,
    save_auth,
    validate_credentials,
)
from app.services.auth.adapter import get_current_user

st.set_page_config(page_title="Login", layout="centered")


auth = get_auth()
if auth.is_authenticated:
    st.success(f"✅ Sudah login sebagai **{get_current_user()}**")
    st.stop()


def on_login_submit(username: str, password: str):
    """Callback: Validate credentials & update state."""
    config = AuthConfig.instance()
    users = config.get_users_dict()

    # Check if auth enabled
    if not config.is_enabled():
        # Dev mode: auto-login
        user_data = get_default_user(users)
        if user_data:
            auth_session = get_auth()
            auth_session.login(user_data["username"], user_data["role"])
            save_auth(auth_session)
            st.success("✅ Login berhasil (dev mode)")
            st.rerun()
        return

    # Production mode: validate credentials
    user_data = validate_credentials(username, password, users)

    if user_data:
        auth_session = get_auth()
        auth_session.login(user_data["username"], user_data["role"])
        save_auth(auth_session)
        st.success("✅ Login berhasil")
        st.rerun()
    else:
        st.error("❌ Username atau password salah")


st.header("Login", divider=True)


@st.fragment
def login_form():
    """Login form as fragment - only this reruns on submit."""
    with st.form("login_form"):
        username = st.text_input(
            label="Username",
            placeholder="Masukkan username Anda",
        )
        password = st.text_input(
            label="Password",
            type="password",
            placeholder="Masukkan password Anda",
        )
        submit = st.form_submit_button("Login", use_container_width=True)

    if submit:
        # Validate empty input
        if not username.strip():
            st.toast("❌ Username tidak boleh kosong")
            return
        if not password.strip():
            st.toast("❌ Password tidak boleh kosong")
            return

        # Call callback
        on_login_submit(username, password)


# Render login form
login_form()


# ============================================================================
# INFO SECTION
# ============================================================================
with st.expander("Info Login"):
    st.write("""
        - Gunakan username dan password yang sudah didaftarkan di file `secrets.toml`.
        - Jika belum memiliki akun, silakan hubungi administrator sistem.
    """)
