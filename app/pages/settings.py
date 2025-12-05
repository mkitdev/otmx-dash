"""place holder settings page."""

import streamlit as st

from app.services.auth import require_login, require_role

require_login()
require_role("administrator")
st.write("Ini adalah halaman Settings")
