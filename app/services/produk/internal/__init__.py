"""Internal module exports - only used by adapter.py.

Do not import from external consumers (pages, other services).
"""

from app.services.produk.internal.queries import (
    aggregate_by_catatan,
    aggregate_by_final_status,
    aggregate_by_jenis,
)
from app.services.produk.internal.repository import ProductRepository

__all__ = [
    "ProductRepository",
    "aggregate_by_catatan",
    "aggregate_by_final_status",
    "aggregate_by_jenis",
]
