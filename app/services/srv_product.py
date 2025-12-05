from datetime import timedelta
from pathlib import Path

import pandas as pd
import streamlit as st
from loguru import logger

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
MOCK_CSV = DATA_DIR / "mock_data_produk.csv"

# [ ] TODO: Later migrate to sql server


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


@st.cache_data(ttl=timedelta(minutes=10))
def load_product_data() -> pd.DataFrame:
    """Load product data from csv with fallback to mock data."""
    try:
        return _read_csv(MOCK_CSV)
    except Exception as exc:
        logger.error(f"Gagal muat mock data: {exc}")
        return pd.DataFrame()
