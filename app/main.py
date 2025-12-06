import streamlit as st

from app.core.mlog import setup_logging
from app.services.auth.adapter import get_auth
from app.services.utils import track_user_visit_page

if "logger" not in st.session_state:
    st.session_state.logger = setup_logging()
logger = st.session_state.logger

st.set_page_config(
    page_title="Otmx Dash",
    page_icon=":shark:",
    layout="wide",
    initial_sidebar_state="auto",
    menu_items={
        "About": "Aplikasi dashboard untuk Software Otomax",
        "Get Help": "https://www.otomax-software.com/id",
        "Report a bug": "https://wa.me/6285777076575",
    },
)
st.logo(
    image=".streamlit/otomax_logo.png",
    link="https://www.otomax-software.com/id",
)

# Initialize authentication state (adapter auto-initializes via get_auth)
auth = get_auth()

# Counter to track app reruns
if "page_main_counter" not in st.session_state:
    st.session_state.page_main_counter = 0


# PAGE DEFINITIONS
login_pg = st.Page("pages/auth/login.py", title="Login")
logout_pg = st.Page("pages/auth/logout.py", title="Logout")
landing = st.Page("pages/other/landing.py", title="Home", default=True)
produk = st.Page("pages/reports/produk.py", title="Produk")
reseller = st.Page("pages/reports/reseller.py", title="Reseller")
adm_settings = st.Page("pages/settings.py", title="Settings")


# NAVIGATION ROUTING
if auth.is_authenticated:
    # Build navigation based on role
    nav_config = {
        "Welcome": [landing],
        "Reports": [produk, reseller],
        "Account": [logout_pg],
    }

    # Only add Admin section if user is administrator
    if auth.role == "administrator":
        nav_config["Admin"] = [adm_settings]

    pg = st.navigation(nav_config)
else:
    pg = st.navigation({
        "Account": [login_pg],
    })


# TRACK PAGE VISIT
current_title = pg.title if hasattr(pg, "title") else None

if current_title:
    track_user_visit_page(current_title)


# [ ] TODO: DEBUG: SESSION STATE (remove in production)
with st.sidebar:
    st.json(st.session_state, expanded=False)

# EXECUTE PAGE

st.session_state.page_main_counter += 1
pg.run()
