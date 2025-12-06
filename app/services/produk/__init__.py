"""Product module - domain, adapter, and internal repository layer.

Public API:
- State management: get_produk_state(), save_produk_state()
- Data access: get_product_data_cached()
- Summaries: get_summary_by_*_cached() functions
- Domain: ProductLoadState

Internal (do not import directly):
- ProductRepository, query functions → use via adapter layer
"""

from app.services.produk.adapter import (
    get_product_data_cached,
    get_produk_state,
    get_summary_by_catatan_cached,
    get_summary_by_final_status_cached,
    get_summary_by_jenis_cached,
    save_produk_state,
)
from app.services.produk.state import ProductLoadState

__all__ = [
    # Domain
    "ProductLoadState",
    # State management
    "get_produk_state",
    "save_produk_state",
    # Data access
    "get_product_data_cached",
    # Summaries
    "get_summary_by_catatan_cached",
    "get_summary_by_jenis_cached",
    "get_summary_by_final_status_cached",
]
