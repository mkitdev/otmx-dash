"""Halaman Produk dengan lazy loading pattern."""

from datetime import datetime

import streamlit as st
import streamlit_shadcn_ui as ui

from app.core.mlog import log_user_event
from app.services.auth_guard import require_login
from app.services.sql_product import get_product_data

require_login()


def _init_produk_state():
    """Initialize flags only. Data loaded from cache, not stored in state."""
    if "produk_is_loaded" not in st.session_state:
        st.session_state.produk_is_loaded = False

    if "produk_is_loading" not in st.session_state:
        st.session_state.produk_is_loading = False

    if "produk_error" not in st.session_state:
        st.session_state.produk_error = None

    if "produk_last_update" not in st.session_state:
        st.session_state.produk_last_update = None


_init_produk_state()


def on_load_data_produk():
    """Callback: Load data produk dari cache, update flag.

    Flow: Clear state → Load from cache → Update flags & timestamp
    Jangan render UI di sini.
    """
    # Clear previous state
    st.session_state.produk_is_loaded = False
    st.session_state.produk_error = None

    # Start loading
    st.session_state.produk_is_loading = True
    log_user_event(
        event="user load_data_produk",
        user_id=st.session_state.get("auth_username", "user"),
        role=st.session_state.get("auth_user_role", "user"),
        message="user Load Data Produk",
    )
    try:
        get_product_data()

        # Update state
        st.session_state.produk_is_loaded = True
        st.session_state.produk_last_update = datetime.now()

    except FileNotFoundError as e:
        st.session_state.produk_error = f"File tidak ditemukan: {e!s}"
        st.session_state.produk_is_loaded = False

    except ValueError as e:
        st.session_state.produk_error = f"Data tidak valid: {e!s}"
        st.session_state.produk_is_loaded = False

    except Exception as e:
        st.session_state.produk_error = f"Error: {e!s}"
        st.session_state.produk_is_loaded = False

    finally:
        st.session_state.produk_is_loading = False


def on_clear_cache():
    """callback: Clear cache data produk."""
    get_product_data.clear()
    st.session_state.produk_is_loaded = False
    st.session_state.produk_error = None
    st.session_state.produk_last_update = None
    log_user_event(
        event="user clear_cache_produk",
        user_id=st.session_state.get("auth_username", "user"),
        role=st.session_state.get("auth_user_role", "user"),
        message="user Clear Cache Produk",
    )


# UI HEADER


st.header("Data Produk", divider=True)


# SIDEBAR CONTROLS

with st.sidebar:
    st.button(
        label="📥 Muat Data",
        on_click=on_load_data_produk,
        type="primary",
        disabled=st.session_state.produk_is_loading,
        width="stretch",
    )

    st.button(
        label="🗑️ Clear Cache",
        on_click=on_clear_cache,
        type="secondary",
        width="stretch",
    )

    if st.session_state.produk_is_loading:
        st.spinner("Loading...")

    if st.session_state.produk_error:
        st.warning(st.session_state.produk_error)

    # Show last update time
    if st.session_state.produk_last_update:
        st.caption(
            f"Terakhir diperbarui: {st.session_state.produk_last_update.strftime('%H:%M:%S')}"
        )


# MAIN CONTENT


def render_statitics_ui():
    """Render statistik produk dalam bentuk cards."""
    with st.container():
        with st.expander(
            label="Lihat Statistik Produk", expanded=False, width="stretch"
        ):
            st.dataframe(
                data=df,
                width="stretch",
                hide_index=False,
            )
        col1, col2, col3 = st.columns(spec=3)
        with col1:
            ui.card(
                title="Total Operator",
                content=str(df["opr_kode"].nunique()),
                description="Jumlah operator unik dalam sistem",
            ).render()
        with col2:
            ui.card(
                title="Total Operator Tersedia",
                content=str(len(df[df["opr_status"] == "available"])),
                description="Jumlah operator yang berstatus tersedia",
            ).render()
        with col3:
            ui.card(
                title="Total Operator Tidak Tersedia",
                content=str(len(df[df["opr_status"] == "unavailable"])),
                description="Jumlah operator yang berstatus tidak tersedia",
            ).render()


if st.session_state.produk_is_loaded:
    # Get data dari cache (bukan dari state)
    df = get_product_data()

    if df.empty:
        st.warning("Data produk kosong")
    else:
        render_statitics_ui()


else:
    st.info("👇 Klik tombol **Muat Data Produk** di sidebar untuk memulai.")
