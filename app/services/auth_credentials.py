"""Authentication credentials validation - pure functions.

State management is handled at UI layer (pages), not here.
This module only validates credentials and returns data.
"""

from app.core.mlog import log_user_event


def validate_credentials(
    username: str,
    password: str,
    users_dict: dict,
) -> dict | None:
    """Validate username & password against users dictionary.

    Args:
        username: Username to validate
        password: Password to validate
        users_dict: Dictionary of users from secrets.toml

    Returns:
        User data dict {username, role} if valid, None if invalid

    Side effects:
        Logs login attempts (success/failed)
    """
    if not username or not password:
        return None

    for user_data in users_dict.values():
        if username == user_data.get("username") and password == user_data.get(
            "password"
        ):
            log_user_event("login_success", user_id=username)
            return {
                "username": username,
                "role": user_data.get("role", "user"),
            }

    log_user_event("login_failed", user_id=username)
    return None


def get_default_user(users_dict: dict) -> dict | None:
    """Get default user for dev mode (when auth is disabled).

    Args:
        users_dict: Dictionary of users from secrets.toml

    Returns:
        User data dict {username, role} or None if default user not found

    Side effects:
        Logs dev mode auto-login
    """
    default_user = "admin"
    user_data = users_dict.get(default_user, {})

    if user_data:
        log_user_event("login_bypass", user_id=default_user)
        return {
            "username": user_data.get("username", default_user),
            "role": user_data.get("role", "user"),
        }

    return None
