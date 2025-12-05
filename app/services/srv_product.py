from datetime import timedelta
from pathlib import Path

import pandas as pd
import streamlit as st
from loguru import logger

from app.core.mlog import log_app

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
MOCK_CSV = DATA_DIR / "mock_data_produk.csv"

# [ ] TODO: Later migrate to sql server


@st.cache_data(ttl=timedelta(minutes=10))
def get_product_data() -> pd.DataFrame:
    """Load product data dari mock CSV.

    Function ini di-cache selama 10 menit untuk performa.

    Nanti ketika actual data siap (SQL Server), ganti function ini
    untuk query dari database.
    """
    try:
        if not MOCK_CSV.exists():
            raise FileNotFoundError(f"Mock data tidak ditemukan: {MOCK_CSV}")

        df = pd.read_csv(MOCK_CSV)
        log_app(f"Loaded mock data produk: {len(df)} rows")

    except Exception as exc:
        logger.error(f"Error membaca mock data produk: {exc}")
        return pd.DataFrame()
    return df
