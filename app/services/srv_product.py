from datetime import timedelta
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

from app.core.mlog import log_app

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
MOCK_CSV = DATA_DIR / "mock_data_produk.csv"


@st.cache_data(ttl=timedelta(minutes=10), show_spinner="Memuat data produk...")
def get_product_data() -> pd.DataFrame:
    """Load + normalisasi data produk langsung via DuckDB.

    UI layer hanya menerima hasil akhir, tidak ada transform di luar.

    Returns:
        pd.DataFrame: Data produk yang sudah dinormalisasi
    """
    try:
        if not MOCK_CSV.exists():
            raise FileNotFoundError(f"Mock data tidak ditemukan: {MOCK_CSV}")

        sql = f"""
        SELECT
            opr_kode,
            opr_nama,

            -- NORMALISASI OPERATOR STATUS
            CASE
                WHEN opr_gangguan = 0 AND opr_kosong = 0 THEN 'available'
                ELSE 'unavailable'
            END AS opr_status,

            prd_kode,
            prd_name,

            -- NORMALISASI PRODUK STATUS
            CASE
                WHEN prd_stts_aktif = 1 THEN 'aktif'
                WHEN prd_stts_gangguan = 1 THEN 'gangguan'
                WHEN prd_stts_kosong = 1 THEN 'kosong'
                ELSE 'nonaktif'
            END AS prd_status,

            -- NORMALISASI JENIS PRODUK
            CASE
                WHEN prd_jenis_postpaid = 1 THEN 'postpaid'
                WHEN prd_jenis_fisik = 1 THEN 'fisik'
                WHEN prd_jenis_unit = 1 THEN 'unit'
                ELSE 'reguler'
            END AS prd_jenis,

            harga_jual

        FROM read_csv_auto('{MOCK_CSV.as_posix()}')
        """

        df = duckdb.sql(sql).df()

        if df.empty:
            raise ValueError("Data produk kosong setelah normalisasi")

        log_app("Loaded mock product data", row_count=len(df))

    except Exception as e:
        log_app("Failed to load product data", error=str(e))
        raise  # UI yang handle error
    return df
