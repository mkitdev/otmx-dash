import streamlit as st

from app.core.mlog import log_user_event


def track_page(pg):
    current_title = pg.title if hasattr(pg, "title") else ""

    if "current_page" not in st.session_state:
        st.session_state.current_page = None

    if current_title != st.session_state.current_page:
        log_user_event(
            "page_visit",
            user_id=st.session_state.get("auth_username", "guest"),
            page=current_title if current_title is not None else "",
            referrer=st.session_state.current_page or "start",
        )

        st.session_state.current_page = current_title
