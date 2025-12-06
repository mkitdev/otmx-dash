"""Authentication adapter - dict ⇆ AuthSession bridge for Streamlit.

Converts between:
- Streamlit session_state dict format
- AuthSession domain object
"""

import streamlit as st

from app.services.auth._internal.config import AuthConfig
from app.services.auth._internal.credentials import (
    get_default_user,
    validate_credentials,
)
from app.services.auth.session import AuthSession


def get_auth() -> AuthSession:
    """Get current auth session (from state or create new).

    Deserializes auth state from session_state dict → AuthSession object.
    Initializes if first time, using config for enabled flag.

    Returns:
        AuthSession: Current user's auth state
    """
    if "auth" not in st.session_state:
        config = AuthConfig.instance()
        st.session_state.auth = {
            "is_authenticated": False,
            "username": None,
            "role": None,
            "enabled": config.is_enabled(),
        }

    return AuthSession.from_dict(st.session_state.auth)


def save_auth(auth: AuthSession) -> None:
    """Save auth session to session_state.

    Serializes AuthSession object → session_state dict.
    Called after login/logout to persist state.

    Args:
        auth: AuthSession to persist
    """
    st.session_state.auth = auth.to_dict()


def get_current_user() -> str | None:
    """Get current authenticated user's username.

    Returns:
        str: Username if authenticated, None otherwise
    """
    auth = get_auth()
    return auth.username if auth.is_authenticated else None


def get_current_user_role() -> str | None:
    """Get current authenticated user's role.

    Returns:
        str: Role if authenticated, None otherwise
    """
    auth = get_auth()
    return auth.role if auth.is_authenticated else None


def perform_login(username: str, password: str) -> dict | None:
    """Perform login with credentials validation.

    Validates username & password against configured users.
    For dev mode (auth disabled), attempts auto-login with default user.

    Args:
        username: Username to login with (empty string for dev mode)
        password: Password to login with (empty string for dev mode)

    Returns:
        dict: User data {username, role} if login successful, None otherwise
    """
    config = AuthConfig.instance()
    users = config.get_users_dict()

    # Dev mode: auth disabled
    if not config.is_enabled():
        return get_default_user(users)

    # Production mode: validate credentials
    return validate_credentials(username, password, users)
