import streamlit as st
from services.auth import get_current_user, init_auth_state, logout, require_login

init_auth_state()

require_login()

st.title("Logout")

st.write(f"Login sebagai: **{get_current_user()}**")

if st.button("Logout"):
    logout()
    st.success("Berhasil logout")
    st.rerun()
