from datetime import timedelta

import duckdb
import pandas as pd
import streamlit as st
from loguru import logger

from app.core.db_manager import get_conn

# =========================
# RAW SQL (TANPA LOGIC BISNIS)
# =========================

SQL_QUERY = """
select
    opr.kode   as opr_kode,
    opr.nama   as opr_nama,
    opr.gangguan as opr_gangguan,
    opr.kosong   as opr_kosong,
    COALESCE(opr.catatan,'UNSET') as opr_catatan,

    prd.kode   as prd_kode,
    prd.nama   as prd_name,
    prd.aktif    as prd_stts_aktif,
    prd.gangguan as prd_stts_gangguan,
    prd.kosong   as prd_stts_kosong,

    prd.postpaid as prd_jenis_postpaid,
    prd.fisik    as prd_jenis_fisik,
    COALESCE(prd.unit, 0) as prd_jenis_unit,
    prd.harga_jual

from produk as prd
join operator as opr on prd.kode_operator = opr.kode
"""


# =========================
# DUCKDB TRANSFORMATION
# =========================


def _transform_product_data(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Normalisasi & business rule layer via DuckDB."""
    # guard if df_raw is empty
    if df_raw.empty:
        return df_raw
    return duckdb.sql(
        """
        SELECT
            *,

            -- OPERATOR STATUS (DERIVED)
            CASE
                WHEN opr_gangguan = 0 AND opr_kosong = 0
                THEN 'available'
                ELSE 'unavailable'
            END AS opr_status,

            -- PRODUCT STATUS (DERIVED, LOCAL)
            CASE
                WHEN prd_stts_aktif = 1
                 AND prd_stts_gangguan = 0
                 AND prd_stts_kosong = 0
                THEN 'available'
                ELSE 'unavailable'
            END AS prd_status,

            -- FINAL PRODUCT STATUS (GLOBAL RESOLUTION)
            CASE
                WHEN opr_gangguan = 1 OR opr_kosong = 1 THEN 'unavailable'
                WHEN prd_stts_gangguan = 1 OR prd_stts_kosong = 1 THEN 'unavailable'
                WHEN prd_stts_aktif = 0 THEN 'unavailable'
                ELSE 'available'
            END AS prd_status_final,

            -- PRODUCT TYPE
            CASE
                WHEN prd_jenis_postpaid = 1 AND prd_jenis_fisik = 0 THEN 'postpaid'
                WHEN prd_jenis_postpaid = 0 AND prd_jenis_fisik = 1 THEN 'fisik'
                WHEN prd_jenis_postpaid = 0 AND prd_jenis_fisik = 0 THEN 'reguler'
                WHEN prd_jenis_postpaid = 1 AND prd_jenis_fisik = 1 THEN 'undefined'
            END AS prd_jenis

        FROM df_raw
        """
    ).to_df()


# =========================
# PUBLIC SERVICE FUNCTION
# =========================


@st.cache_data(ttl=timedelta(minutes=10), show_spinner="Memuat data produk...")
def get_product_data() -> pd.DataFrame:
    """Load data produk (RAW SQL → DuckDB Transform)."""
    try:
        conn = get_conn()
        df_raw = conn.query(SQL_QUERY)

        if df_raw.empty:
            logger.warning("Product data is empty")
            return df_raw

        df = _transform_product_data(df_raw)

        logger.info(f"Loaded & transformed product data: {len(df)} rows")

    except Exception:
        logger.error("Failed to load product data", exc_info=True)
        raise
    return df
