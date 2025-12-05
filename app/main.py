import streamlit as st

from app.services.auth import init_auth_state
from app.services.tracking import track_page_visit

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
init_auth_state()

# this is the counter to track app_reruns
if "app_rerun_counter" not in st.session_state:
    st.session_state.app_rerun_counter = 0

login_pg = st.Page("pages/login.py", title="Login")
logout_pg = st.Page("pages/logout.py", title="Logout")


landing = st.Page("pages/landing.py", title="Home", default=True)
produk = st.Page("pages/produk.py", title="Produk")
reseller = st.Page("pages/reseller.py", title="Reseller")

login_pg = st.Page("pages/login.py", title="Login")
logout_pg = st.Page("pages/logout.py", title="Logout")
adm_settings = st.Page("pages/settings.py", title="Settings")

if st.session_state.get("auth_is_authenticated"):
    # Build navigation based on role
    nav_config = {
        "Welcome": [landing],
        "Data": [produk, reseller],
        "Account": [logout_pg],
    }

    # Only add Admin section if user is administrator
    if st.session_state.get("auth_user_role") == "administrator":
        nav_config["Admin"] = [adm_settings]

    pg = st.navigation(nav_config)
else:
    pg = st.navigation({
        "Account": [login_pg],
    })


current_title = pg.title if hasattr(pg, "title") else None

# Track page visit
if current_title:
    track_page_visit(current_title)

with st.sidebar:
    st.json(st.session_state)

st.session_state.app_rerun_counter += 1
pg.run()
