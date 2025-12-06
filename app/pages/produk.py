"""Halaman Produk dengan lazy loading pattern."""

import streamlit as st

from app.core.mlog import log_user_event
from app.services.auth import (
    get_current_user,
    get_current_user_role,
    require_login,
)
from app.services.produk import (
    get_product_data_cached,
    get_produk_state,
    get_summary_by_catatan_cached,
    get_summary_by_final_status_cached,
    get_summary_by_jenis_cached,
    save_produk_state,
)
from app.services.produk._internal.queries import (
    count_total_unique_catatan,
    count_total_unique_operator,
    count_total_unique_produk,
)

require_login()
# for debuging : hitung berapa kali page ini di load
if "page_produk_counter" not in st.session_state:
    st.session_state.page_produk_counter = 0


def on_load_data_produk():
    """Callback: Load data produk dari cache, update state.

    Flow: Get state → Start loading → Load from cache → Update state
    """
    state = get_produk_state()
    state.start_loading()
    save_produk_state(state)

    log_user_event(
        event="user load_data_produk",
        user_id=get_current_user() or "user",
        role=get_current_user_role() or "user",
        message="user Load Data Produk",
    )
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

    Streamlit clears cache automatically on page rerun,
    we just reset the state flags here.
    """
    state = get_produk_state()
    state.clear_cache()
    save_produk_state(state)

    log_user_event(
        event="user clear_cache_produk",
        user_id=get_current_user() or "user",
        role=get_current_user_role() or "user",
        message="user Clear Cache Produk",
    )


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


# MAIN CONTENT
st.header("Data Produk", divider=True)


def render_statistics_ui():
    """Render statistik produk dalam bentuk cards & tables."""
    # Get raw data untuk card metrics
    df_raw = get_product_data_cached()

    # Card metrics - inline count functions
    col1, col2, col3 = st.columns(3, gap="small")

    with col1:
        total_operator = count_total_unique_operator(df_raw)
        st.metric("👥 Total Operator", total_operator)

    with col2:
        total_catatan = count_total_unique_catatan(df_raw)
        st.metric("📋 Total Catatan", total_catatan)

    with col3:
        total_produk = count_total_unique_produk(df_raw)
        st.metric("📦 Total Produk", total_produk)

    st.divider()

    # Summary by Catatan (Operator Notes)
    st.subheader("📋 Ringkasan per Catatan Operator")
    summary_catatan = get_summary_by_catatan_cached()
    st.dataframe(summary_catatan, use_container_width=True, hide_index=True)

    # Summary by Jenis (Product Type)
    st.subheader("📦 Ringkasan per Jenis Produk")
    summary_jenis = get_summary_by_jenis_cached()
    st.dataframe(summary_jenis, use_container_width=True, hide_index=True)

    # Summary by Final Status
    st.subheader("✅ Ringkasan per Status Final")
    summary_status = get_summary_by_final_status_cached()
    st.dataframe(summary_status, use_container_width=True, hide_index=True)


if state.is_loaded:
    # Get data dari cache (bukan dari state)
    df = get_product_data_cached()

    if df.empty:
        st.warning("Data produk kosong")
    else:
        render_statistics_ui()

        # Show detailed data table
        st.subheader("📊 Detail Data Produk")
        st.dataframe(
            data=df,
            use_container_width=True,
            hide_index=False,
        )

else:
    st.info("👇 Klik tombol **Muat Data Produk** di sidebar untuk memulai.")

st.session_state.page_produk_counter += 1
