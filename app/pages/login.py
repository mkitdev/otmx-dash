import streamlit as st
from services.auth import get_current_user, init_auth_state, login

init_auth_state()

st.set_page_config(page_title="Login", layout="centered")
st.title("Login")


# Jika sudah login, langsung redirect
if st.session_state.get("auth_is_authenticated"):
    st.success(f"Sudah login sebagai {get_current_user()}")
    st.stop()


@st.fragment
def login_form():
    """Login form as fragment - only this rerun on submit, not full page."""
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

        # Try to login
        if login(username, password):
            st.success("✅ Login berhasil")
            st.rerun()
        else:
            st.toast("❌ Username atau password salah")


# Render login form
login_form()

# Info section
with st.expander("Info Login"):
    st.write(
        """
        - Gunakan username dan password yang sudah didaftarkan di file `secrets.toml`.
        - Jika belum memiliki akun, silakan hubungi administrator sistem.
        """
    )
