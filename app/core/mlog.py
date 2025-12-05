"""setup loguru and related logging features."""
# [ ] TODO : Later Kalau santai pindahn ke log_config.yaml ya

import functools
import inspect
import logging
import sys
import time
from collections.abc import Callable
from pathlib import Path

from loguru import logger

# Setup log directory
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


# Intercept standard logging ke loguru
class InterceptHandler(logging.Handler):
    """Handler untuk intercept standard logging ke loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit log record ke loguru."""
        # Get corresponding Loguru level
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def timeit(func: Callable):
    """Decorator to measure execution time using high-precision timer.

    Args:
        func (callable): The function to be timed.

    Returns:
        callable: The wrapped function with timing.
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.debug(
            "Function '{}' executed in {:.4f}s",
            func.__name__,
            elapsed,
        )
        return result

    return wrapped


def logger_wraps(*, entry: bool = True, exit: bool = True, level: str = "DEBUG"):
    """Decorator untuk wrap function dengan entry/exit logging.

    Args:
        entry (bool): Log pada entry. Default True.
        exit (bool): Log pada exit. Default True.
        level (str): Log level. Default "DEBUG".

    Returns:
        callable: Wrapper function
    """

    def wrapper(func):  # noqa: ANN001
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            if entry:
                logger.log(
                    level,
                    "→ Entering {} with args={}, kwargs={}",
                    func.__name__,
                    args,
                    kwargs,
                )
            result = func(*args, **kwargs)
            if exit:
                logger.log(level, "← Exiting {} with result={}", func.__name__, result)
            return result

        return wrapped

    return wrapper


def log_user(message: str, user_id: str = "guest", action: str = "", **kwargs):
    """Log user action — high-level perspective.

    Args:
        message (str): User-friendly message
        user_id (str): User identifier. Default "guest".
        action (str): Action description. Default "".
        **kwargs: Additional context

    Example:
        >>> log_user(
        ...     "🔄 Data refresh triggered",
        ...     user_id="user123",
        ...     action="refresh_data",
        ... )
    """
    logger.bind(user_id=user_id, action=action, **kwargs).info(message)


def log_app(message: str, **kwargs):
    """Log app action — technical perspective.

    Args:
        message (str): Technical message
        **kwargs: Additional context (row_count, duration, status, etc)

    Example:
        >>> log_app(
        ...     "Fetching data from database",
        ...     row_count=150,
        ...     duration=0.45,
        ... )
    """
    logger.bind(**kwargs).debug(message)


def log_page_visit(page_title: str, user_id: str = "guest", **kwargs):
    """Log user page visit — track posisi user di aplikasi.

    Args:
        page_title (str): Nama/title page yang dibuka
        user_id (str): User identifier. Default "guest".
        **kwargs: Additional context (timestamp, referrer, dll)

    Example:
        >>> log_page_visit(
        ...     "Produk",
        ...     user_id="user123",
        ...     referrer="Home",
        ... )
    """
    logger.bind(user_id=user_id, page=page_title, **kwargs).info(
        "📋 User visited page: {}", page_title
    )


def log_user_activity(
    activity_type: str, user_id: str = "guest", page: str = "", **kwargs
):
    """Log detailed user activity — general purpose activity tracking.

    Args:
        activity_type (str): Tipe activity (e.g., 'button_click', 'search', 'filter')
        user_id (str): User identifier. Default "guest".
        page (str): Current page. Default "".
        **kwargs: Additional context (target, value, duration, dll)

    Example:
        >>> log_user_activity(
        ...     "button_click",
        ...     user_id="user123",
        ...     page="Produk",
        ...     target="filter_by_category",
        ...     value="Electronics",
        ... )
    """
    logger.bind(user_id=user_id, page=page, activity=activity_type, **kwargs).info(
        "🔔 User activity: {}", activity_type
    )


def setup_logging(to_file: bool = True):
    """Setup loguru dengan dual logging: user + app perspective.

    Args:
        to_file (bool): Write logs to file. Default True.

    Handlers:
    - logs/app.log → Combined log file (if to_file=True)
    - stderr → Console dengan color

    Format:
    - File: timestamp | level | module:function:line | context | message
    - Console: Colorful untuk development

    Rotation:
    - 500 MB per file
    - Retention: 7 days
    """
    # Remove default stderr handler
    logger.remove()

    # ========== FILE HANDLER ==========
    if to_file:
        logger.add(
            LOG_DIR / "app.log",
            level="DEBUG",
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}:{function}:{line}</cyan> | "
                "<magenta>{extra}</magenta> | "
                "<level>{message}</level>"
            ),
            rotation="500 MB",
            retention="7 days",
            enqueue=True,
            backtrace=True,
            diagnose=False,  # Set to False in production to avoid leaking sensitive data
        )

    # ========== CONSOLE HANDLER ==========
    logger.add(
        sys.stderr,
        level="DEBUG",
        format=(
            "<green>{time:HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}:{function}:{line}</cyan> | "
            "<magenta>{extra}</magenta> | "
            "<level>{message}</level>"
        ),
        colorize=True,
        enqueue=True,
        diagnose=True,
    )
