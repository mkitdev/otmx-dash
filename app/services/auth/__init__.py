"""Authentication module - domain, adapter, and guards."""

# Import from auth/ submodule files
from app.services.auth.adapter import get_auth, save_auth
from app.services.auth.config import AuthConfig
from app.services.auth.guard import require_login, require_role
from app.services.auth.session import AuthSession

__all__ = [
    "AuthConfig",
    "AuthSession",
    "get_auth",
    "require_login",
    "require_role",
    "save_auth",
]
