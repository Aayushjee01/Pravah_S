"""Structured logging configuration for the application.

Sets up JSON-formatted logging with appropriate levels based on
the application environment.
"""

import logging
import sys

from app.core.config import get_settings


def setup_logging() -> logging.Logger:
    """Configure and return the application logger.

    Returns:
        A configured logger instance for the application.
    """
    settings = get_settings()

    # Create logger
    logger = logging.getLogger("house_price_predictor")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler with formatting
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    # Format: timestamp - level - module - message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# Module-level logger instance
logger = setup_logging()
