"""
backend/utils/logger.py
========================
Centralised logging configuration for the entire backend.
Writes to both console (stdout) and a rotating log file.

Usage:
    from backend.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Something happened")
"""

import logging
import logging.handlers
import sys
from pathlib import Path


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger for the given module name.
    Log level and log directory are read from the Config class.
    This function is safe to call before the Flask app is initialised.
    """
    # Import here to avoid circular imports
    try:
        from backend.config import Config
        log_level = getattr(logging, Config.LOG_LEVEL, logging.INFO)
        log_dir = Config.LOG_DIR
    except Exception:
        log_level = logging.INFO
        log_dir = Path("logs")

    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if the logger is already configured
    if logger.handlers:
        return logger

    logger.setLevel(log_level)

    # ── Console handler ───────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    # ── Rotating file handler ─────────────────────────────
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10 MB per file
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(log_level)
        file_fmt = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_fmt)
        logger.addHandler(file_handler)
    except (OSError, PermissionError) as exc:
        # Non-fatal: just log to console if file logging fails
        logger.warning("Could not create log file: %s", exc)

    return logger

