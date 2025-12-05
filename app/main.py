import streamlit as st

from app.core.mlog import log_app, log_user, setup_logging

setup_logging(to_file=True)
st.write("Hello, Otomax Dash!")

# test logging
st.button("Click me", on_click=lambda: st.write("Button clicked!"))
log_app("App started", event="app_start")
log_user("User accessed the dashboard", user_id="user_001", action="access_dashboard")
