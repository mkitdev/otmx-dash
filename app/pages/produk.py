"""Halaman Produk dengan lazy loading pattern."""

import streamlit as st
import streamlit_shadcn_ui as ui

from app.core.mlog import log_user_event
from app.services.auth.adapter import get_current_user, get_current_user_role
from app.services.auth.guard import require_login
from app.services.produk import get_produk_state, save_produk_state
from app.services.sql_product import get_product_data

require_login()
# for debuging : hitung berapa kali page ini di load
if "page_produk_load_count" not in st.session_state:
    st.session_state.page_produk_load_count = 0
st.session_state.page_produk_load_count += 1


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
        get_product_data()
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
    """Callback: Clear cache data produk & reset state."""
    get_product_data.clear()

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

    if state.last_update:
        st.caption(f"Terakhir diperbarui: {state.last_update.strftime('%H:%M:%S')}")


# MAIN CONTENT
st.header("Data Produk", divider=True)


def render_statitics_ui():
    """Render statistik produk dalam bentuk cards."""
    with st.container():
        with st.expander(
            label=f"list product with last update {state.last_update.strftime('%H:%M:%S') if state.last_update else 'N/A'}",
            expanded=False,
        ):
            st.dataframe(
                data=df,
                width="stretch",
                hide_index=False,
            )
        card_cols = st.columns(3, gap="large")
        with card_cols[0]:
            ui.metric_card(
                title="Total Operator",
                content=str(df["opr_kode"].nunique()),
                description="Jumlah operator unik dalam sistem",
                key="total_operator_card",
            )
        with card_cols[1]:
            ui.metric_card(
                title="Total Operator Tersedia",
                content=str(len(df[df["opr_status"] == "available"])),
                description="Jumlah operator yang berstatus tersedia",
                key="total_operator_tersedia_card",
            )
        with card_cols[2]:
            ui.metric_card(
                title="Total Operator Tidak Tersedia",
                content=str(len(df[df["opr_status"] == "unavailable"])),
                description="Jumlah operator yang berstatus tidak tersedia",
                key="total_operator_tidak_tersedia_card",
            )


if state.is_loaded:
    # Get data dari cache (bukan dari state)
    df = get_product_data()

    if df.empty:
        st.warning("Data produk kosong")
    else:
        render_statitics_ui()

else:
    st.info("👇 Klik tombol **Muat Data Produk** di sidebar untuk memulai.")
