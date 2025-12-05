import streamlit as st

from app.core.mlog import log_user_event, setup_logging

st.set_page_config(
    page_title="Otmx Dash",
    page_icon=":shark:",
    layout="wide",
)

if "logging_initialized" not in st.session_state:
    setup_logging(to_file=True)
    log_user_event("app_start")
    st.session_state.logging_initialized = True

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "auth_username" not in st.session_state:
    st.session_state.auth_username = None

if "current_page" not in st.session_state:
    st.session_state.current_page = None

if "last_page" not in st.session_state:
    st.session_state.last_page = None


def do_login():
    """Callback function untuk login."""
    st.session_state.logged_in = True
    st.session_state.auth_username = "admin"
    log_user_event(f"User {st.session_state.auth_username} logged in")


def do_logout():
    """Callback function untuk logout."""
    log_user_event(f"User {st.session_state.auth_username} logged out")
    st.session_state.logged_in = False
    st.session_state.auth_username = None


# =========================
# PAGE DEFINITIONS
# =========================
def login_page():
    """Halaman login."""
    st.title("Login")
    st.button("Log in", on_click=do_login)


def logout_page():
    """Halaman logout."""
    st.title("Logout")
    st.button("Log out", on_click=do_logout)


landing = st.Page("pages/landing.py", title="Home", default=True)
produk = st.Page("pages/produk.py", title="Produk")
reseller = st.Page("pages/reseller.py", title="Reseller")

login_pg = st.Page(login_page, title="Login")
logout_pg = st.Page(logout_page, title="Logout")


if st.session_state.logged_in:
    pg = st.navigation({
        "Welcome": [landing],
        "Data": [produk, reseller],
        "Account": [logout_pg],
    })
else:
    pg = st.navigation({
        "Account": [login_pg],
    })


current_title = pg.title if hasattr(pg, "title") else None

if current_title != st.session_state.current_page:
    log_user_event(
        current_title or "Unknown",
        user_id=st.session_state.auth_username or "guest",
        referrer=st.session_state.current_page or "start",
    )

    st.session_state.last_page = st.session_state.current_page
    st.session_state.current_page = current_title

with st.sidebar:
    st.json(st.session_state)

# =========================
# RUN PAGE
# =========================
pg.run()
