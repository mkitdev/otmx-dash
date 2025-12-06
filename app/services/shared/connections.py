"""Database connection management — shared utilities."""

import streamlit as st
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import BackEndServiceError


@st.cache_resource(show_time=True)
def get_conn():
    """Get database connection — cached sebagai RESOURCE.

    Resource cache karena:
    - connection object adalah stateful
    - tidak perlu di-serialize
    - lifetime = session user
    - jangan di-reset setiap rerun
    """
    try:
        logger.debug("Initializing SQL connection resource...")
        conn = st.connection(name="sql")
        logger.info("SQL connection resource initialized")
    except SQLAlchemyError as e:
        logger.error(f"Connection failed: {e}", exc_info=True)
        backend_exc = BackEndServiceError(service_name="database_connection", error=e)
        raise backend_exc from e
    return conn
