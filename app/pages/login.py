import streamlit as st
from services.auth import get_current_user, init_auth_state, login

init_auth_state()

st.title("Login")

# Jika sudah login, langsung redirect
if st.session_state.get("auth_is_authenticated"):
    st.success(f"Sudah login sebagai {get_current_user()}")
    st.stop()

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login")

if submit:
    if login(username, password):
        st.success("Login berhasil")
        st.rerun()
    else:
        st.error("Username atau password salah")
