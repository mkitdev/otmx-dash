import streamlit as st

from app.core.mlog import log_page_visit, log_user, setup_logging

# Initialize logging only once
if "logging_initialized" not in st.session_state:
    setup_logging(to_file=True)
    log_user("Application started")
    st.session_state.logging_initialized = True

st.set_page_config(
    page_title="Otmx Dash",
    page_icon=":shark:",
    layout="wide",
    menu_items={
        "Get Help": "https://www.extremelycoolapp.com/help",
        "Report a bug": "https://www.extremelycoolapp.com/bug",
        "About": "# This is a header. This is an *extremely* cool app!",
    },
)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.auth_username = None
    st.session_state.user_current_page = None

if "auth_username" not in st.session_state:
    st.session_state.auth_username = None
if "user_current_page" not in st.session_state:
    st.session_state.user_current_page = "login"


def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.session_state.auth_username = "admin"
        log_user(f"User {st.session_state.auth_username} logged in")

        st.rerun()


def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.auth_username = None
        st.rerun()


# sidebar navigation
with st.sidebar:
    st.json(st.session_state)

login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

landing = st.Page(
    "pages/landing.py", title="Home", icon=":material/home:", default=True
)
produk = st.Page("pages/produk.py", title="Produk", icon=":material/storefront:")
reseller = st.Page(
    "pages/reseller.py", title="Reseller", icon=":material/people_outline:"
)

if st.session_state.logged_in:
    pg = st.navigation({
        "welcome": [landing],
        "data": [produk, reseller],
        "Account": [logout_page],
    })
else:
    pg = st.navigation({"Account": [login_page]})

# Track page visit
if hasattr(pg, "title") and pg.title:
    current_page = pg.title
    if "last_page" not in st.session_state:
        st.session_state.last_page = None

    # Jika page berubah, log page visit
    if st.session_state.last_page != current_page:
        log_page_visit(
            current_page,
            user_id=st.session_state.auth_username or "guest",
            referrer=st.session_state.last_page or "start",
        )
        st.session_state.last_page = current_page

pg.run()
