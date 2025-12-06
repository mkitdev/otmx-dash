"""Product query functions - pure aggregation via pandas.

All functions:
- Take transformed product data (with derived columns)
- Perform aggregation using pandas (simple, readable)
- Return aggregated results as pd.DataFrame or dict
- No side effects, deterministic

Internal module - only imported by adapter.py, not exposed to UI.
"""

import pandas as pd
from loguru import logger


def get_stats_from_df(df: pd.DataFrame) -> dict:
    """Extract key statistics from transformed product dataframe.

    Fast pandas operations (no DuckDB needed for simple counts).

    Args:
        df: Transformed product DataFrame (must have derived columns like prd_status_final)

    Returns:
        dict: Statistics with keys:
            - total_operator: Count of unique operators
            - total_produk: Count of unique products
            - total_catatan: Count of unique catatan
            - total_available: Count of available products
            - total_unavailable: Count of unavailable products
    """
    if df.empty:
        logger.warning("Empty dataframe provided to get_stats_from_df")
        return {
            "total_operator": 0,
            "total_produk": 0,
            "total_catatan": 0,
            "total_available": 0,
            "total_unavailable": 0,
        }

    try:
        # Use pandas for simple operations - much faster than DuckDB for this
        stats = {
            "total_operator": int(df["opr_kode"].nunique()),
            "total_produk": int(df["prd_kode"].nunique()),
            "total_catatan": int(df["opr_catatan"].nunique()),
            "total_available": len(
                df[df["prd_status_final"] == "available"]["prd_kode"].unique()
            ),
            "total_unavailable": len(
                df[df["prd_status_final"] == "unavailable"]["prd_kode"].unique()
            ),
        }
        logger.info(f"Extracted stats from dataframe: {stats}")
        return stats

    except Exception as e:
        logger.error(f"Failed to extract stats from dataframe: {e}", exc_info=True)
        raise


def aggregate_by_catatan(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate product data by operator notes (catatan) from transformed dataframe.

    Groups data and calculates:
    - total_operator: Count of unique operators
    - total_produk: Count of unique products

    Args:
        df: Transformed product DataFrame

    Returns:
        pd.DataFrame: Aggregated data grouped by opr_catatan, sorted by total_produk desc
    """
    if df.empty:
        logger.warning("Empty dataframe provided to aggregate_by_catatan")
        return df

    try:
        result = (
            df.groupby("opr_catatan")
            .agg(
                total_operator=("opr_kode", "nunique"),
                total_produk=("prd_kode", "nunique"),
            )
            .reset_index()
            .sort_values("total_produk", ascending=False)
        )

        logger.info(f"Aggregated by catatan: {len(result)} rows")
        return result

    except Exception as e:
        logger.error(f"Failed to aggregate by catatan: {e}", exc_info=True)
        raise


def aggregate_by_jenis(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate product data by product type (jenis) from transformed dataframe.

    Groups data and calculates:
    - total_operator: Count of unique operators
    - total_produk: Count of unique products

    Args:
        df: Transformed product DataFrame

    Returns:
        pd.DataFrame: Aggregated data grouped by prd_jenis, sorted by total_produk desc
    """
    if df.empty:
        logger.warning("Empty dataframe provided to aggregate_by_jenis")
        return df

    try:
        result = (
            df.groupby("prd_jenis")
            .agg(
                total_operator=("opr_kode", "nunique"),
                total_produk=("prd_kode", "nunique"),
            )
            .reset_index()
            .sort_values("total_produk", ascending=False)
        )

        logger.info(f"Aggregated by jenis: {len(result)} rows")
        return result

    except Exception as e:
        logger.error(f"Failed to aggregate by jenis: {e}", exc_info=True)
        raise


def aggregate_by_final_status(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate product data by final status from transformed dataframe.

    Groups data and calculates:
    - total_operator: Count of unique operators
    - total_produk: Count of unique products

    Args:
        df: Transformed product DataFrame

    Returns:
        pd.DataFrame: Aggregated data by status (available/unavailable), sorted by total_produk desc
    """
    if df.empty:
        logger.warning("Empty dataframe provided to aggregate_by_final_status")
        return df

    try:
        result = (
            df.groupby("prd_status_final")
            .agg(
                total_operator=("opr_kode", "nunique"),
                total_produk=("prd_kode", "nunique"),
            )
            .reset_index()
            .rename(columns={"prd_status_final": "status"})
            .sort_values("total_produk", ascending=False)
        )

        logger.info(f"Aggregated by final_status: {len(result)} rows")
        return result

    except Exception as e:
        logger.error(f"Failed to aggregate by final_status: {e}", exc_info=True)
        raise
