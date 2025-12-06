"""Authentication module - domain, adapter, and guards.

Public API:
- State management: get_auth(), save_auth()
- User accessors: get_current_user(), get_current_user_role()
- Login flow: perform_login(username, password)
- Access guards: require_login(), require_role()
- Domain: AuthSession

Internal (do not import directly):
- AuthConfig, validate_credentials, get_default_user → use via adapter layer
"""

# Import from auth/ submodule files
from app.services.auth.adapter import (
    get_auth,
    get_current_user,
    get_current_user_role,
    perform_login,
    save_auth,
)
from app.services.auth.guard import require_login, require_role
from app.services.auth.session import AuthSession

__all__ = [
    # Domain
    "AuthSession",
    # State management
    "get_auth",
    "save_auth",
    # User accessors
    "get_current_user",
    "get_current_user_role",
    # Login flow
    "perform_login",
    # Access guards
    "require_login",
    "require_role",
]
