"""Product query functions - pure aggregation via DuckDB.

All functions:
- Take raw product data from repository
- Perform aggregation using DuckDB (consistent with infrastructure layer)
- Return aggregated results as pd.DataFrame
- No side effects, deterministic

Internal module - only imported by adapter.py, not exposed to UI.
"""

import duckdb
import pandas as pd
from loguru import logger


def aggregate_by_catatan(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Aggregate product data by operator notes (catatan) via DuckDB.

    Groups raw data and calculates:
    - total_operator: Count of unique operators
    - total_produk: Count of unique products
    - total_available: Count of available products

    Args:
        df_raw: Raw product DataFrame from ProductRepository.get_raw_products()

    Returns:
        pd.DataFrame: Aggregated data grouped by opr_catatan, sorted by total_produk desc
    """
    if df_raw.empty:
        logger.warning("Empty dataframe provided to aggregate_by_catatan")
        return df_raw

    try:
        result = duckdb.sql(
            """
            SELECT
                opr_catatan,
                COUNT(DISTINCT opr_kode) as total_operator,
                COUNT(DISTINCT prd_kode) as total_produk
            FROM df_raw
            GROUP BY opr_catatan
            ORDER BY total_produk DESC
            """
        ).to_df()

        logger.info(f"Aggregated by catatan: {len(result)} rows")

    except Exception as e:
        logger.error(f"Failed to aggregate by catatan: {e}", exc_info=True)
        raise
    return result


def aggregate_by_jenis(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Aggregate product data by product type (jenis) via DuckDB.

    Groups raw data and calculates:
    - total_operator: Count of unique operators
    - total_produk: Count of unique products
    - total_available: Count of available products

    Args:
        df_raw: Raw product DataFrame from ProductRepository.get_raw_products()

    Returns:
        pd.DataFrame: Aggregated data grouped by prd_jenis, sorted by total_produk desc
    """
    if df_raw.empty:
        logger.warning("Empty dataframe provided to aggregate_by_jenis")
        return df_raw

    try:
        # First transform to add prd_jenis column
        df_with_jenis = duckdb.sql(
            """
            SELECT
                *,
                CASE
                    WHEN prd_jenis_postpaid = 1 AND prd_jenis_fisik = 0 THEN 'postpaid'
                    WHEN prd_jenis_postpaid = 0 AND prd_jenis_fisik = 1 THEN 'fisik'
                    WHEN prd_jenis_postpaid = 0 AND prd_jenis_fisik = 0 THEN 'reguler'
                    WHEN prd_jenis_postpaid = 1 AND prd_jenis_fisik = 1 THEN 'undefined'
                END AS prd_jenis
            FROM df_raw
            """
        ).to_df()

        # Then aggregate
        result = duckdb.sql(
            """
            SELECT
                prd_jenis,
                COUNT(DISTINCT opr_kode) as total_operator,
                COUNT(DISTINCT prd_kode) as total_produk
            FROM df_with_jenis
            GROUP BY prd_jenis
            ORDER BY total_produk DESC
            """
        ).to_df()

        logger.info(f"Aggregated by jenis: {len(result)} rows")

    except Exception as e:
        logger.error(f"Failed to aggregate by jenis: {e}", exc_info=True)
        raise
    return result


def aggregate_by_final_status(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Aggregate product data by final status via DuckDB.

    Groups raw data and calculates:
    - total_operator: Count of unique operators
    - total_produk: Count of unique products

    Note: Requires final status logic to be in raw data or calculated here.

    Args:
        df_raw: Raw product DataFrame from ProductRepository.get_raw_products()

    Returns:
        pd.DataFrame: Aggregated data by status (available/unavailable), sorted by total_produk desc
    """
    if df_raw.empty:
        logger.warning("Empty dataframe provided to aggregate_by_final_status")
        return df_raw

    try:
        # Add final status calculation
        df_with_status = duckdb.sql(
            """
            SELECT
                *,
                CASE
                    WHEN opr_gangguan = 1 OR opr_kosong = 1 THEN 'unavailable'
                    WHEN prd_stts_gangguan = 1 OR prd_stts_kosong = 1 THEN 'unavailable'
                    WHEN prd_stts_aktif = 0 THEN 'unavailable'
                    ELSE 'available'
                END AS prd_status_final
            FROM df_raw
            """
        ).to_df()

        # Then aggregate
        result = duckdb.sql(
            """
            SELECT
                prd_status_final,
                COUNT(DISTINCT opr_kode) as total_operator,
                COUNT(DISTINCT prd_kode) as total_produk
            FROM df_with_status
            GROUP BY prd_status_final
            ORDER BY total_produk DESC
            """
        ).to_df()

        logger.info(f"Aggregated by final_status: {len(result)} rows")

    except Exception as e:
        logger.error(f"Failed to aggregate by final_status: {e}", exc_info=True)
        raise
    return result
