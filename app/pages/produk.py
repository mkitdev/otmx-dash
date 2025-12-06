"""Halaman Produk dengan lazy loading pattern."""

import datetime
from typing import Any

import streamlit as st
import streamlit_shadcn_ui as ui

from app.components import metric_card_custom
from app.core.mlog import log_user_event
from app.services.auth import (
    get_current_user,
    get_current_user_role,
    require_login,
)
from app.services.produk import (
    clear_product_cache,
    get_product_data_cached,
    get_produk_state,
    get_summary_by_catatan_cached,
    get_summary_by_final_status_cached,
    get_summary_by_jenis_cached,
    save_produk_state,
)
from app.services.produk._internal.queries import get_stats_from_df

require_login()
# for debuging : hitung berapa kali page ini di load
if "page_produk_counter" not in st.session_state:
    st.session_state.page_produk_counter = 0


def _log_event(event: str, message: str) -> None:
    """Helper: Log user event."""
    log_user_event(
        event=event,
        user_id=get_current_user() or "user",
        role=get_current_user_role() or "user",
        message=message,
    )


def on_load_data_produk():
    """Callback: Load data produk dari cache, update state.

    Flow: Get state → Start loading → Load from cache → Update state
    """
    state = get_produk_state()
    state.start_loading()
    save_produk_state(state)
    _log_event("user load_data_produk", "user Load Data Produk")

    try:
        get_product_data_cached()
        state = get_produk_state()
        state.load_success()
        save_produk_state(state)

    except FileNotFoundError as e:
        state = get_produk_state()
        state.load_failed(f"File tidak ditemukan: {e!s}")
        save_produk_state(state)

    except ValueError as e:
        state = get_produk_state()
        state.load_failed(f"Data tidak valid: {e!s}")
        save_produk_state(state)

    except Exception as e:
        state = get_produk_state()
        state.load_failed(f"Error: {e!s}")
        save_produk_state(state)


def on_clear_cache():
    """Callback: Clear cache data produk & reset state.

    Calls clear_product_cache() to clear only produk-related caches,
    not affecting other modules like reseller, settings, etc.
    """
    clear_product_cache()
    state = get_produk_state()
    state.clear_cache()
    save_produk_state(state)
    _log_event("user clear_cache_produk", "user Clear Cache Produk")


# INITIALIZE STATE
state = get_produk_state()

# SIDEBAR CONTROLS
with st.sidebar:
    st.button(
        label="📥 Muat Data",
        on_click=on_load_data_produk,
        type="primary",
        disabled=state.is_loading,
        width="stretch",
    )

    st.button(
        label="🗑️ Clear Cache",
        on_click=on_clear_cache,
        type="secondary",
        width="stretch",
    )

    if state.is_loading:
        st.spinner("Loading...")

    if state.error:
        st.warning(state.error)


def render_header():
    """Render header section dengan title dan badges."""
    st.header("Data Produk", divider=True)
    ui.badges(badge_list=[("SQL Server Data", "default")])


def render_statistics_ui(df: Any) -> None:
    """Render statistik produk dalam bentuk cards & tables.

    Args:
        df: DataFrame produk yang sudah di-cache
    """
    # Extract stats once using pandas
    stats = get_stats_from_df(df)

    # Row 1: Operator, Produk, Catatan
    col1, col2, col3 = st.columns(3, gap="small")

    with col1:
        metric_card_custom(
            title="Operator",
            content=str(stats["total_operator"]),
            description="Total Group Operator",
            color="blue",
        )

    with col2:
        metric_card_custom(
            title="Produk",
            content=str(stats["total_produk"]),
            description="Total Produk",
            color="green",
        )

    with col3:
        metric_card_custom(
            title="Catatan",
            content=str(stats["total_catatan"]),
            description="Total Catatan",
            color="orange",
        )

    # Row 2: Available, Unavailable
    col4, col5 = st.columns(2, gap="small")

    with col4:
        metric_card_custom(
            title="Available",
            content=str(stats["total_available"]),
            description="Produk Tersedia",
            color="green",
        )

    with col5:
        metric_card_custom(
            title="Unavailable",
            content=str(stats["total_unavailable"]),
            description="Produk Tidak Tersedia",
            color="red",
        )

    # Summary by Catatan (Operator Notes)
    # Format last_update to show only up to seconds

    format_last_update_time()
    with st.expander("Ringksan Berdasarkan pada Kolom Catatan"):
        summary_catatan = get_summary_by_catatan_cached()
        st.dataframe(summary_catatan, width="stretch", hide_index=True)

    # Summary by Jenis (Product Type)
    with st.expander("Lihat Ringkasan per Jenis Produk (flagging di table produk)"):
        summary_jenis = get_summary_by_jenis_cached()
        st.dataframe(summary_jenis, width="stretch", hide_index=True)

    # Summary by Final Status
    with st.expander("Lihat Ringkasan per Status Final (kombinasi opr dan produk)"):
        summary_status = get_summary_by_final_status_cached()
        st.dataframe(summary_status, width="stretch", hide_index=True)


def format_last_update_time():
    """Format time."""
    last_update_str = str(state.last_update)
    try:
        # Try to parse and format
        last_update_dt = datetime.datetime.fromisoformat(last_update_str)
        last_update_str = last_update_dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        # Fallback to string
        pass
    st.caption(f"data refreshed at {last_update_str}")


render_header()
if state.is_loaded:
    # Get data dari cache (bukan dari state)
    df = get_product_data_cached()

    if df.empty:
        st.warning("Data produk kosong")
    else:
        render_statistics_ui(df)

        # Show detailed data table
        with st.expander("Lihat Data Produk Lengkap"):
            st.dataframe(
                data=df,
                width="stretch",
                hide_index=False,
            )

else:
    st.info("👇 Klik tombol **Muat Data Produk** di sidebar untuk memulai.")

st.session_state.page_produk_counter += 1
