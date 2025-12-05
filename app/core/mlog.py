"""setup loguru and related logging features."""
# [ ] TODO : Later Kalau santai pindahn ke log_config.yaml ya

import sys
from pathlib import Path

from loguru import logger

LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logging(to_file: bool = True):
    """Initialize logging once at app startup."""
    logger.remove()

    # ======================
    # CONSOLE (DEV)
    # ======================
    logger.add(
        sys.stderr,
        level="DEBUG",
        format=(
            "<green>{time:HH:mm:ss}</green> | "
            "<level>{level}</level> | "
            "{message} | <magenta>{extra}</magenta>"
        ),
        colorize=True,
    )

    if not to_file:
        return

    # ======================
    # APPLICATION LOG
    # ======================
    logger.add(
        LOG_DIR / "application.log",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        filter=lambda record: record["extra"].get("type") == "app",
        format="{time} | {level} | {message} | {extra}",
        enqueue=True,
    )

    # ======================
    # USER ACTIVITY LOG
    # ======================
    logger.add(
        LOG_DIR / "user_activity.log",
        level="INFO",
        rotation="10 MB",
        retention="7 days",
        filter=lambda record: record["extra"].get("type") == "user",
        format="{time} | {level} | {message} | {extra}",
        enqueue=True,
    )


# =========================
# APPLICATION / SYSTEM LOG
# =========================
def log_app(message: str, **kwargs):
    """Use this logging for system logging.

    For:
    - fetch data
    - cache
    - db access
    - internal flow
    - error & performance (later)
    """
    logger.bind(type="app", **kwargs).debug(message)


# =========================
# USER EVENT (SINGLE ENTRY)
# =========================
def log_user_event(
    event: str,
    user_id: str = "guest",
    page: str = "",
    **kwargs,
):
    """Use this logging for user events.

    For:
    - login / logout
    - page visit
    - button click
    - filter change
    - refresh
    """
    logger.bind(
        type="user",
        event=event,
        user_id=user_id,
        page=page,
        **kwargs,
    ).info(event)
