"""Login page with state management."""

import streamlit as st

from app.pages.auth.auth_guard import get_current_user, init_auth_state, is_auth_enabled
from app.services.auth import get_default_user, validate_credentials

st.set_page_config(page_title="Login", layout="centered")

# ============================================================================
# STATE INITIALIZATION (UI Layer responsibility)
# ============================================================================
init_auth_state()


# ============================================================================
# REDIRECT IF ALREADY AUTHENTICATED
# ============================================================================
if st.session_state.get("auth_is_authenticated"):
    st.success(f"✅ Sudah login sebagai **{get_current_user()}**")
    st.stop()


# ============================================================================
# CALLBACK - LOGIN LOGIC
# ============================================================================
def on_login_submit(username: str, password: str):
    """Callback: Validate credentials & update state."""
    users = st.secrets.get("users", {})

    # Check if auth enabled
    if not is_auth_enabled():
        # Dev mode: auto-login
        user_data = get_default_user(users)
        if user_data:
            st.session_state.auth_username = user_data["username"]
            st.session_state.auth_user_role = user_data["role"]
            st.session_state.auth_is_authenticated = True
            st.success("✅ Login berhasil (dev mode)")
            st.rerun()
        return

    # Production mode: validate credentials
    user_data = validate_credentials(username, password, users)

    if user_data:
        st.session_state.auth_username = user_data["username"]
        st.session_state.auth_user_role = user_data["role"]
        st.session_state.auth_is_authenticated = True
        st.success("✅ Login berhasil")
        st.rerun()
    else:
        st.error("❌ Username atau password salah")


# ============================================================================
# UI - LOGIN FORM
# ============================================================================
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
with st.expander("ℹ️ Info Login"):
    st.write("""
        - Gunakan username dan password yang sudah didaftarkan di file `secrets.toml`.
        - Jika belum memiliki akun, silakan hubungi administrator sistem.
    """)
