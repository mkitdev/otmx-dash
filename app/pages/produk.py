"""Halaman Produk dengan lazy loading pattern."""

from datetime import datetime

import streamlit as st
import streamlit_shadcn_ui as ui

from app.services.auth_guard import require_login
from app.services.srv_product import get_product_data

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
        st.session_state.produk_last_update = None  # Track last load time


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

    try:
        get_product_data()  # From cache, service validates data

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


# UI HEADER

st.header("Data Produk", divider=True)


# SIDEBAR CONTROLS

with st.sidebar:
    st.subheader("Kontrol")

    st.button(
        label="📥 Muat Data Produk",
        on_click=on_load_data_produk,
        type="primary",
        disabled=st.session_state.produk_is_loading,
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

if st.session_state.produk_is_loaded:
    # Get data dari cache (bukan dari state)
    df = get_product_data()

    if df.empty:
        st.warning("Data produk kosong")
    else:
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            ui.card(
                title="Total Produk",
                content=str(len(df)),
                description="Jumlah total produk dalam sistem",
            ).render()
        with col2:
            ui.card(
                title="Aktif",
                content=str(len(df[df["prd_stts_aktif"] == 1])),
                description="Jumlah produk yang berstatus aktif",
            ).render()
        with col3:
            ui.card(
                title="Gangguan",
                content=str(len(df[df["prd_stts_gangguan"] == 1])),
                description="Jumlah produk yang berstatus gangguan",
            ).render()

        with st.expander("Lihat Data Produk Mentah"):
            st.dataframe(
                data=df,
                width="stretch",
                hide_index=True,
            )

else:
    st.info("👇 Klik tombol **Muat Data Produk** di sidebar untuk memulai.")
