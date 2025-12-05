"""Halaman Produk dengan lazy loading pattern."""

import streamlit as st

from app.services.auth import require_login
from app.services.srv_product import get_product_data

require_login()

# ============================================================================
# STATE INITIALIZATION (sesuai guide: flat keys, di awal file)
# ============================================================================
if "produk_df" not in st.session_state:
    st.session_state.produk_df = None

if "produk_is_loaded" not in st.session_state:
    st.session_state.produk_is_loaded = False

if "produk_is_loading" not in st.session_state:
    st.session_state.produk_is_loading = False

if "produk_error" not in st.session_state:
    st.session_state.produk_error = None


# ============================================================================
# CALLBACK (hanya ubah state, tidak render UI)
# ============================================================================
def on_load_data_produk():
    """Callback: Load data produk ke session state. Jangan render UI di sini."""
    st.session_state.produk_is_loading = True
    st.session_state.produk_error = None

    try:
        df = get_product_data()

        if df.empty:
            st.session_state.produk_error = "Data produk kosong"
            st.session_state.produk_is_loaded = False
        else:
            st.session_state.produk_df = df
            st.session_state.produk_is_loaded = True

    except Exception as e:
        st.session_state.produk_error = f"Error: {e!s}"
        st.session_state.produk_is_loaded = False
    finally:
        st.session_state.produk_is_loading = False


# ============================================================================
# UI HEADER
# ============================================================================
st.title("📦 Produk")

# ============================================================================
# SIDEBAR: BUTTON TO LOAD DATA (lazy loading trigger)
# ============================================================================
with st.sidebar:
    st.button(
        label="📥 Muat Data Produk",
        on_click=on_load_data_produk,
        type="primary",
        use_container_width=True,
        disabled=st.session_state.produk_is_loading,
    )

    if st.session_state.produk_is_loading:
        st.spinner("Loading...")

    if st.session_state.produk_error:
        st.error(st.session_state.produk_error)

# ============================================================================
# MAIN: RENDER DATA HANYA JIKA SUDAH DI-LOAD
# ============================================================================
if st.session_state.produk_is_loaded and st.session_state.produk_df is not None:
    # Guard: pastikan data tersedia
    df = st.session_state.produk_df

    # Display info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Produk", len(df))

    # Display data
    st.subheader("Data Produk")
    st.dataframe(df, use_container_width=True, height=400)

else:
    # State: data belum di-load
    st.info("👇 Klik tombol **Muat Data Produk** di sidebar untuk memuat data.")
