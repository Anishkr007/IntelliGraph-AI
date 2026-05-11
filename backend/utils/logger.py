"""
logger.py — Workflow Logger
============================
Provides a consistent logger used across all backend modules.
Logs are written to console AND a rotating file (workflow.log).
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "workflow.log")


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger for the given module name.

    Usage:
        from backend.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Node executed")
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # Already configured — avoid duplicate handlers

    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler — force UTF-8 so emoji chars don't crash on Windows cp1252
    import sys, io
    stream = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace") \
        if hasattr(sys.stdout, "buffer") else sys.stdout
    console = logging.StreamHandler(stream)
    console.setLevel(logging.INFO)
    console.setFormatter(fmt)
    logger.addHandler(console)

    # Rotating file handler (max 5 MB, keep 3 backups)
    try:
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(fmt)
        logger.addHandler(file_handler)
    except Exception:
        pass  # If file logging fails, console logging still works

    return logger
