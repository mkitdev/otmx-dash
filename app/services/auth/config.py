"""Authentication configuration - secrets wrapper with caching."""

import streamlit as st

from app.core.mlog import log_app


class AuthConfig:
    """Centralized auth configuration from secrets.toml (cached).

    Provides type-safe access to:
    - Feature flag: authentication.enable
    - User credentials: users dict
    """

    def __init__(self):
        """Initialize from st.secrets (called once per session via cache)."""
        self._auth_config = st.secrets.get("authentication", {})
        self._users_dict = st.secrets.get("users", {})
        self._is_enabled = self._auth_config.get("enable", True)

        log_app(f"AuthConfig initialized: enabled={self._is_enabled}")

    @staticmethod
    @st.cache_resource
    def instance() -> "AuthConfig":
        """Get singleton instance (cached).

        Returns:
            AuthConfig: Cached instance
        """
        return AuthConfig()

    def is_enabled(self) -> bool:
        """Check if authentication feature is enabled.

        Returns:
            bool: True if auth enabled, False if disabled (dev mode)
        """
        return self._is_enabled

    def get_users_dict(self) -> dict:
        """Get users credentials dictionary.

        Returns:
            dict: Users dict from secrets {username: {username, password, role}}
        """
        return self._users_dict
