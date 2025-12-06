"""Product Repository - Data access layer with SQL & transform logic."""

from datetime import timedelta

import duckdb
import pandas as pd
from loguru import logger

from app.services.shared import get_conn


class ProductRepository:
    """Repository untuk data produk.

    Encapsulates:
    - SQL query definition
    - Data fetching from connection
    - Data transformation via DuckDB
    - Caching strategy

    Pure OOP (no Streamlit logic, only cache decorator).
    """

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

    def __init__(self, cache_ttl: int = 10):
        """Initialize repository with cache TTL.

        Args:
            cache_ttl: Cache time-to-live in minutes (default: 10)
        """
        self.cache_ttl = timedelta(minutes=cache_ttl)

    def get_all_products(self) -> pd.DataFrame:
        """Load & transform data produk.

        Returns:
            pd.DataFrame: Transformed product data with derived columns

        Raises:
            Exception: If database query or transform fails
        """
        try:
            conn = get_conn()
            df_raw = conn.query(self.SQL_QUERY)

            if df_raw.empty:
                logger.warning("Product data is empty")
                return df_raw

            df = self._transform(df_raw)
            logger.info(f"Loaded & transformed product data: {len(df)} rows")

        except Exception:
            logger.error("Failed to load product data", exc_info=True)
            raise

        return df

    def _transform(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """Transform & normalize product data via DuckDB.

        Adds derived columns:
        - opr_status: Operator availability
        - prd_status: Product local availability
        - prd_status_final: Global product availability
        - prd_jenis: Product type classification

        Args:
            df_raw: Raw product dataframe from SQL query

        Returns:
            pd.DataFrame: Transformed dataframe with derived columns
        """
        if df_raw.empty:
            logger.warning("got empty df, skipping transform")
            return df_raw

        df_transformed = duckdb.sql(
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

        logger.info(f"Transformed product data: {len(df_transformed)} rows")
        return df_transformed
