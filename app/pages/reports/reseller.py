"""sample page reseller."""

import streamlit as st
import streamlit_shadcn_ui as ui

from app.components import metric_card_custom
from app.services.auth import require_login

st.write("Ini adalah halaman Reseller")
# every page have this
require_login()


# for debuging : hitung berapa kali page ini di load
if "page_reseller_counter" not in st.session_state:
    st.session_state.page_reseller_counter = 0

st.session_state.page_reseller_counter += 1

# main area :

tab_reseller = ui.tabs(
    options=[
        "summary",
        "downline",
    ],
    default_value="summary",
    key="tabs_reseller",
)
# 1 tabs
if tab_reseller == "summary":
    metric_card_custom(
        title="Total Reseller",
        content="150",
        description="Jumlah reseller aktif",
    )
    cols = st.columns(3)

    with cols[0]:
        metric_card_custom(
            title="Reseller Aktif",
            content="150",
            description="Jumlah reseller aktif",
        )
    with cols[1]:
        metric_card_custom(
            title="Reseller not Active",
            content="25",
            description="Reseller yang bergabung bulan ini",
            color="red",
        )
    with cols[2]:
        metric_card_custom(
            title="Reseller Suspended",
            content="120",
            description="Reseller yang aktif bulan ini",
            color="yellow",
        )
