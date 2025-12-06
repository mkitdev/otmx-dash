"""Halaman Produk dengan lazy loading pattern."""

import streamlit as st
import streamlit_shadcn_ui as ui

from app.core.mlog import log_user_event
from app.services.auth.adapter import get_current_user, get_current_user_role
from app.services.auth.guard import require_login
from app.services.produk import get_product_data, get_produk_state, save_produk_state

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


# MAIN CONTENT
st.header("Data Produk", divider=True)


def render_statitics_ui():
    """Render statistik produk dalam bentuk cards."""
    card_cols = st.columns(3, gap="small")
    with card_cols[0]:
        ui.metric_card(
            title="Total Operator",
            content=str(df["opr_kode"].nunique()),
            description="Jumlah operator unik dalam sistem",
            key="card_total_operator",
        )
    with card_cols[1]:
        ui.metric_card(
            title="Total Produk",
            content=str(df["prd_kode"].nunique()),
            description="Jumlah produk yang berstatus tersedia",
            key="total_produk_tersedia_card",
        )
    with card_cols[2]:
        ui.metric_card(
            title="Total Jenis Catatan",
            content=str(df["opr_catatan"].nunique()),
            description="Jumlah produk yang berstatus tidak tersedia",
            key="total_produk_tidak_tersedia_card",
        )


@st.fragment
def filtering_ui(df):
    """Multi-tier filtering UI (3 level)."""
    with st.expander("Filter Produk", expanded=True):
        # =========================
        # TIER 1 — CATATAN OPERATOR
        # =========================
        tier1_options = df["opr_catatan"].dropna().unique().tolist()

        tier1_selected = st.multiselect(
            label="Catatan Operator",
            options=tier1_options,
            default=tier1_options,
        )

        df_t1 = df[df["opr_catatan"].isin(tier1_selected)]

        # =========================
        # TIER 2 — JENIS PRODUK
        # (tergantung TIER 1)
        # =========================
        tier2_options = df_t1["prd_jenis"].dropna().unique().tolist()

        tier2_selected = st.multiselect(
            label="Jenis Produk",
            options=tier2_options,
            default=tier2_options,
        )

        df_t2 = df_t1[df_t1["prd_jenis"].isin(tier2_selected)]

        # =========================
        # TIER 3 — STATUS FINAL
        # (tergantung TIER 1 + 2)
        # =========================
        tier3_options = df_t2["prd_status_final"].dropna().unique().tolist()

        tier3_selected = st.multiselect(
            label="Status Final",
            options=tier3_options,
            default=tier3_options,
        )

        df_final = df_t2[df_t2["prd_status_final"].isin(tier3_selected)]

        # =========================
        # RESULT
        # =========================
        st.dataframe(
            data=df_final,
            width="stretch",
            hide_index=False,
        )


if state.is_loaded:
    # Get data dari cache (bukan dari state)
    df = get_product_data()

    if df.empty:
        st.warning("Data produk kosong")
    else:
        render_statitics_ui()
        filtering_ui(df)

else:
    st.info("👇 Klik tombol **Muat Data Produk** di sidebar untuk memulai.")
st.session_state.page_produk_counter += 1
