import functools
import inspect
import logging
import time
from collections.abc import Callable

from loguru import logger


class InterceptHandler(logging.Handler):
    """Handler untuk intercept standard logging ke loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def logger_wraps(*, entry: bool = True, exit: bool = True, level: str = "DEBUG"):
    """Decorator untuk wrap function dengan entry/exit logging."""

    def wrapper(func):  # noqa: ANN001
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            if entry:
                logger.log(
                    level,
                    "\u2192 Entering {} with args={}, kwargs={}",
                    func.__name__,
                    args,
                    kwargs,
                )
            result = func(*args, **kwargs)
            if exit:
                logger.log(
                    level, "\u2190 Exiting {} with result={}", func.__name__, result
                )
            return result

        return wrapped

    return wrapper


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
