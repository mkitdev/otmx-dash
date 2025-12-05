"""Product load state - pure OOP domain without Streamlit."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProductLoadState:
    """Product data loading state.

    Pure domain object (no Streamlit dependencies).
    Tracks loading status, errors, and cache update time.

    Attributes:
        is_loaded: Whether product data has been successfully loaded
        is_loading: Whether data is currently being loaded
        error: Error message if loading failed
        last_update: Timestamp of last successful load
    """

    is_loaded: bool = False
    is_loading: bool = False
    error: str | None = None
    last_update: datetime | None = None

    def start_loading(self) -> None:
        """Mark loading as started."""
        self.is_loading = True
        self.is_loaded = False
        self.error = None

    def load_success(self, timestamp: datetime | None = None) -> None:
        """Mark loading as successful.

        Args:
            timestamp: When data was loaded (defaults to now)
        """
        self.is_loading = False
        self.is_loaded = True
        self.error = None
        self.last_update = timestamp or datetime.now()

    def load_failed(self, error_message: str) -> None:
        """Mark loading as failed.

        Args:
            error_message: Description of the error
        """
        self.is_loading = False
        self.is_loaded = False
        self.error = error_message

    def clear_cache(self) -> None:
        """Clear all state (for cache reset)."""
        self.is_loaded = False
        self.is_loading = False
        self.error = None
        self.last_update = None

    def to_dict(self) -> dict:
        """Serialize to dictionary for session_state storage.

        Returns:
            dict: State as {is_loaded, is_loading, error, last_update}
        """
        return {
            "is_loaded": self.is_loaded,
            "is_loading": self.is_loading,
            "error": self.error,
            "last_update": self.last_update,
        }

    @staticmethod
    def from_dict(data: dict) -> "ProductLoadState":
        """Deserialize from dictionary.

        Args:
            data: Dictionary with product load state

        Returns:
            ProductLoadState: Reconstructed instance
        """
        return ProductLoadState(
            is_loaded=data.get("is_loaded", False),
            is_loading=data.get("is_loading", False),
            error=data.get("error"),
            last_update=data.get("last_update"),
        )
