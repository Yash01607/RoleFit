import logging
import sys
from pythonjsonlogger import jsonlogger
from app.core.config import settings


def get_logger(name: str) -> logging.Logger:
    """Return a JSON-formatted logger instance with all levels supported."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)

        # Define log format
        log_format = "%(asctime)s %(levelname)s %(name)s %(message)s"
        formatter = jsonlogger.JsonFormatter(
            fmt=log_format,
            json_default=str,        # ensure non-serializable objects become strings
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Log level from .env (default INFO)
        logger.setLevel(settings.LOG_LEVEL.upper())
        logger.propagate = False   # avoid duplicate logs from root logger

    return logger
