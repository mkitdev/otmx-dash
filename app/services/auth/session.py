"""Authentication domain - pure OOP without Streamlit."""

from dataclasses import dataclass


@dataclass
class AuthSession:
    """User authentication session state.

    Pure domain object (no Streamlit dependencies).
    Encapsulates auth state + behavior.

    Attributes:
        is_authenticated: Whether user is logged in
        username: Current logged-in username
        role: Current user's role (for RBAC)
        enabled: Whether auth feature is enabled (from config)
    """

    is_authenticated: bool = False
    username: str | None = None
    role: str | None = None
    enabled: bool = True

    def login(self, username: str, role: str) -> None:
        """Authenticate user.

        Args:
            username: User's login username
            role: User's assigned role
        """
        self.is_authenticated = True
        self.username = username
        self.role = role

    def logout(self) -> None:
        """Deauthenticate user (clear all auth data)."""
        self.is_authenticated = False
        self.username = None
        self.role = None

    def can_access(self, required_role: str) -> bool:
        """Check if user can access resource with required role.

        Admin always has access.

        Args:
            required_role: Required role to access resource

        Returns:
            bool: True if user can access, False otherwise
        """
        if not self.is_authenticated:
            return False

        # Administrator always allowed
        if self.role == "administrator":
            return True

        return self.role == required_role

    def to_dict(self) -> dict:
        """Serialize to dictionary for session_state storage.

        Returns:
            dict: State as {is_authenticated, username, role, enabled}
        """
        return {
            "is_authenticated": self.is_authenticated,
            "username": self.username,
            "role": self.role,
            "enabled": self.enabled,
        }

    @staticmethod
    def from_dict(data: dict) -> "AuthSession":
        """Deserialize from dictionary (reconstructs from session_state).

        Args:
            data: Dictionary with auth state

        Returns:
            AuthSession: Reconstructed instance
        """
        return AuthSession(
            is_authenticated=data.get("is_authenticated", False),
            username=data.get("username"),
            role=data.get("role"),
            enabled=data.get("enabled", True),
        )
