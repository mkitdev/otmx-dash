"""sample page produk."""

import streamlit as st

from app.services.auth import require_login
from app.services.srv_product import load_product_data

require_login()

# states
if "df_produk" not in st.session_state:
    st.session_state.df_produk = None


def load_data_produk():
    """Load data produk and store in session state."""
    st.session_state.df_produk = load_product_data()
    st.success("Data produk berhasil dimuat!")


st.write("Ini adalah halaman Produk")
with st.sidebar:
    btn_load_data = st.button(
        label="Muat Data Produk",
        width="stretch",
        type="primary",
        key="btn_load_data_produk",
        on_click=load_data_produk,
    )
