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


def _validate_query_result(result_row: tuple | None, context: str = "") -> int:
    """Validate DuckDB query result and extract count value.

    Inner function: Raises ValueError if result is None or empty.
    Used by count_total_unique_* functions to validate aggregation results.

    Args:
        result_row: Row tuple from duckdb.sql().fetchone()
        context: Optional context string for logging (e.g., 'operator count')

    Returns:
        int: Count value from first column of result row

    Raises:
        ValueError: If result_row is None (query returned no results)
    """
    if result_row is None:
        msg = f"Query returned no results{f' ({context})' if context else ''}"
        raise ValueError(msg)
    return result_row[0]


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
        ).df()

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
        result = duckdb.sql(
            """
            SELECT
                CASE
                    WHEN prd_jenis_postpaid = 1 AND prd_jenis_fisik = 0 THEN 'postpaid'
                    WHEN prd_jenis_postpaid = 0 AND prd_jenis_fisik = 1 THEN 'fisik'
                    WHEN prd_jenis_postpaid = 0 AND prd_jenis_fisik = 0 THEN 'reguler'
                    WHEN prd_jenis_postpaid = 1 AND prd_jenis_fisik = 1 THEN 'undefined'
                END AS prd_jenis,
                COUNT(DISTINCT opr_kode) as total_operator,
                COUNT(DISTINCT prd_kode) as total_produk
            FROM df_raw
            GROUP BY prd_jenis
            ORDER BY total_produk DESC
            """
        ).df()

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
        result = duckdb.sql(
            """
            SELECT
                CASE
                    WHEN opr_gangguan = 1 OR opr_kosong = 1 THEN 'unavailable'
                    WHEN prd_stts_gangguan = 1 OR prd_stts_kosong = 1 THEN 'unavailable'
                    WHEN prd_stts_aktif = 0 THEN 'unavailable'
                    ELSE 'available'
                END AS prd_status_final,
                COUNT(DISTINCT opr_kode) as total_operator,
                COUNT(DISTINCT prd_kode) as total_produk
            FROM df_raw
            GROUP BY prd_status_final
            ORDER BY total_produk DESC
            """
        ).df()

        logger.info(f"Aggregated by final_status: {len(result)} rows")

    except Exception as e:
        logger.error(f"Failed to aggregate by final_status: {e}", exc_info=True)
        raise
    return result


def count_total_unique_operator(df_raw: pd.DataFrame) -> int:
    """Count total unique operators in raw product data.

    Args:
        df_raw: Raw product DataFrame from ProductRepository.get_raw_products()

    Returns:
        int: Total count of unique operators (opr_kode)
    """
    if df_raw.empty:
        logger.warning("Empty dataframe provided to count_total_unique_operator")
        return 0

    try:
        row = duckdb.sql(
            """
            SELECT COUNT(DISTINCT opr_kode) as total_operator
            FROM df_raw
            """
        ).fetchone()
        result = _validate_query_result(row, "operator count")
    except Exception as e:
        logger.error(f"Failed to count total unique operators: {e}", exc_info=True)
        raise
    else:
        logger.info(f"Counted total unique operators: {result}")
        return result


def count_total_unique_catatan(df_raw: pd.DataFrame) -> int:
    """Count total unique operator notes (catatan) in raw product data.

    Args:
        df_raw: Raw product DataFrame from ProductRepository.get_raw_products()

    Returns:
        int: Total count of unique opr_catatan
    """
    if df_raw.empty:
        logger.warning("Empty dataframe provided to count_total_unique_catatan")
        return 0

    try:
        row = duckdb.sql(
            """
            SELECT COUNT(DISTINCT opr_catatan) as total_catatan
            FROM df_raw
            """
        ).fetchone()
        result = _validate_query_result(row, "catatan count")
    except Exception as e:
        logger.error(f"Failed to count total unique catatan: {e}", exc_info=True)
        raise
    else:
        logger.info(f"Counted total unique catatan: {result}")
        return result


def count_total_unique_produk(df_raw: pd.DataFrame) -> int:
    """Count total unique products in raw product data.

    Args:
        df_raw: Raw product DataFrame from ProductRepository.get_raw_products()

    Returns:
        int: Total count of unique prd_kode
    """
    if df_raw.empty:
        logger.warning("Empty dataframe provided to count_total_unique_produk")
        return 0

    try:
        row = duckdb.sql(
            """
            SELECT COUNT(DISTINCT prd_kode) as total_produk
            FROM df_raw
            """
        ).fetchone()
        result = _validate_query_result(row, "produk count")
    except Exception as e:
        logger.error(f"Failed to count total unique produk: {e}", exc_info=True)
        raise
    else:
        logger.info(f"Counted total unique produk: {result}")
        return result
