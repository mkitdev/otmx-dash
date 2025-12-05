"""Authentication guard functions - DEPRECATED, use app.services.auth instead.

This module is kept for backward compatibility.
All functions are now re-exported from the new auth module.

New code should import from:
    from app.services.auth import require_login, require_role
    from app.services.auth import get_current_user, get_current_user_role
"""

# Re-export from new auth module for backward compatibility
from app.services.auth import (  # noqa: F401
    get_auth,
    require_login,
    require_role,
)
from app.services.auth.adapter import (  # noqa: F401
    get_current_user,
    get_current_user_role,
)


def is_auth_enabled() -> bool:
    """Check if authentication is enabled from secrets.

    DEPRECATED: Use AuthConfig.instance().is_enabled() instead.

    Returns:
        bool: True if auth enabled, False otherwise
    """
    auth = get_auth()
    return auth.enabled
