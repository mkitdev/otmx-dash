"""Product adapter - dict ⇆ ProductLoadState bridge for Streamlit.

Converts between:
- Streamlit session_state dict format
- ProductLoadState domain object
"""

from datetime import timedelta

import streamlit as st

from app.services.produk.repo_main_df import get_product_data
from app.services.produk.state import ProductLoadState


def get_produk_state() -> ProductLoadState:
    """Get current product load state (from state or create new).

    Deserializes from session_state dict → ProductLoadState object.
    Initializes if first time.

    Returns:
        ProductLoadState: Current product load state
    """
    if "produk_state" not in st.session_state:
        st.session_state.produk_state = {
            "is_loaded": False,
            "is_loading": False,
            "error": None,
            "last_update": None,
        }

    return ProductLoadState.from_dict(st.session_state.produk_state)


def save_produk_state(state: ProductLoadState) -> None:
    """Save product load state to session_state.

    Serializes ProductLoadState object → session_state dict.
    Called after state changes (loading, success, error, clear).

    Args:
        state: ProductLoadState to persist
    """
    st.session_state.produk_state = state.to_dict()


@st.cache_data(ttl=timedelta(minutes=10), show_spinner="Memuat data produk...")
def get_product_data_cached():
    """Adapter to make loose to streamlit."""
    return get_product_data()
