"""Login page with state management."""

import streamlit as st

from app.services.auth import (
    get_auth,
    get_current_user,
    perform_login,
    save_auth,
)

st.set_page_config(page_title="Login", layout="centered")


auth = get_auth()
if auth.is_authenticated:
    st.success(f"✅ Sudah login sebagai **{get_current_user()}**")
    st.stop()


def on_login_submit(username: str, password: str):
    """Callback: Validate credentials & update state."""
    user_data = perform_login(username, password)

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
