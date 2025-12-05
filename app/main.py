import streamlit as st

from app.services.auth import init_auth_state, log_user_event

st.set_page_config(
    page_title="Otmx Dash",
    page_icon=":shark:",
    layout="wide",
)

init_auth_state()


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
if "current_page" not in st.session_state:
    st.session_state.current_page = None

if current_title != st.session_state.current_page:
    log_user_event(
        event="page_visit",
        user_id=st.session_state.get("auth_username", "guest"),
        page=current_title if current_title is not None else "",
        referrer=st.session_state.current_page or "start",
        message=f"🔗 Visited {current_title}",
    )

    st.session_state.current_page = current_title

with st.sidebar:
    st.json(st.session_state)


pg.run()
