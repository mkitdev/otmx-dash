"""Product adapter - dict ⇆ ProductLoadState bridge for Streamlit.

Converts between:
- Streamlit session_state dict format
- ProductLoadState domain object
"""

from datetime import timedelta

import streamlit as st

from app.core.mlog_perf import timeit
from app.services.produk._internal.queries import (
    aggregate_by_catatan,
    aggregate_by_final_status,
    aggregate_by_jenis,
)
from app.services.produk._internal.repository import get_all_products
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


@st.cache_data(ttl=timedelta(minutes=0), show_spinner="Memuat data produk...")
def get_product_data_cached():
    """Get product data from repository cache.

    Returns:
        pd.DataFrame: Cached product data with all transformations
    """
    return get_all_products()


@st.cache_data(
    ttl=timedelta(minutes=10), show_spinner="Menyiapkan ringkasan catatan..."
)
@timeit
def get_summary_by_catatan_cached():
    """Get product summary grouped by operator notes (cached).

    Reuses transformed data from cache instead of querying raw data again.

    Returns:
        pd.DataFrame: Summary with columns [opr_catatan, total_operator, total_produk]
    """
    df = get_product_data_cached()  # Reuse cached transformed DF
    return aggregate_by_catatan(df)


@st.cache_data(ttl=timedelta(minutes=10), show_spinner="Menyiapkan ringkasan jenis...")
@timeit
def get_summary_by_jenis_cached():
    """Get product summary grouped by product type (cached).

    Reuses transformed data from cache instead of querying raw data again.

    Returns:
        pd.DataFrame: Summary with columns [prd_jenis, total_operator, total_produk]
    """
    df = get_product_data_cached()  # Reuse cached transformed DF
    return aggregate_by_jenis(df)


@st.cache_data(ttl=timedelta(minutes=10), show_spinner="Menyiapkan ringkasan status...")
@timeit
def get_summary_by_final_status_cached():
    """Get product summary grouped by final status (cached).

    Reuses transformed data from cache instead of querying raw data again.

    Returns:
        pd.DataFrame: Summary with columns [status, total_operator, total_produk]
    """
    df = get_product_data_cached()  # Reuse cached transformed DF
    return aggregate_by_final_status(df)


def clear_product_cache() -> None:
    """Clear only product module's cached data (selective clearing).

    Uses individual func.clear() to clear only produk-related caches,
    NOT affecting other modules' caches like reseller, settings, etc.

    Clears:
    - get_product_data_cached()
    - get_summary_by_catatan_cached()
    - get_summary_by_jenis_cached()
    - get_summary_by_final_status_cached()
    """
    get_product_data_cached.clear()
    get_summary_by_catatan_cached.clear()
    get_summary_by_jenis_cached.clear()
    get_summary_by_final_status_cached.clear()
