"""User activity tracking utilities."""

import streamlit as st

from app.core.mlog import log_user_event


def track_page_visit(current_page: str) -> None:
    """Track page visit when user navigates to a new page.

    Args:
        current_page: Title of the current page being visited
    """
    if "current_page" not in st.session_state:
        st.session_state.current_page = None

    # Only log if page has changed
    if current_page == st.session_state.current_page:
        return

    user = st.session_state.get("auth_username", "guest")
    role = st.session_state.get("auth_user_role", "none")
    referrer = st.session_state.current_page or "start"

    # Log page visit with full context
    log_user_event(
        event="page_visit",
        user_id=user,
        page=current_page or "",
        referrer=referrer,
        role=role,
        message=f"User: {user} (role: {role}) → {current_page}",
    )

    # Update current page tracking
    st.session_state.current_page = current_page
