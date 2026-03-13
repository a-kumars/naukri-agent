"""
Logger utility for Naukri Agent
"""

import logging
import os
from config import LOG_FILE_PATH, LOG_LEVEL, LOG_FORMAT


def setup_logger(name: str = "naukri_agent") -> logging.Logger:
    """
    Setup and return a logger instance

    Args:
        name: Name of the logger

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL.upper()))

    # Remove existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)

    # Create file handler
    file_handler = logging.FileHandler(LOG_FILE_PATH)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger