"""
backend/utils/validators.py
============================
Input validation helpers for file uploads and API request bodies.
Keeps all validation logic in one place for easy testing.
"""

import os
from pathlib import Path
from werkzeug.datastructures import FileStorage
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Maximum file size in bytes (default 50 MB, overridden from Config)
DEFAULT_MAX_BYTES = 50 * 1024 * 1024
ALLOWED_EXTENSIONS = {"csv"}

# Required columns for each dataset type (minimum viable set)
REQUIRED_COLUMNS = {
    "shipments": {
        "shipment_id", "origin_city", "destination_city",
        "scheduled_delivery", "is_delayed",
    },
    "traffic": {
        "route_id", "timestamp", "congestion_level",
    },
    "weather": {
        "city", "timestamp", "condition",
    },
    "gps": {
        "shipment_id", "timestamp", "latitude", "longitude",
    },
}


def allowed_file(filename: str, allowed: set[str] | None = None) -> bool:
    """Return True if the filename has an allowed extension."""
    if allowed is None:
        allowed = ALLOWED_EXTENSIONS
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in allowed
    )


def validate_upload(
    file: FileStorage,
    dataset_type: str,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> tuple[bool, str]:
    """
    Validate a Flask FileStorage object before saving.

    Returns:
        (True, "")          if valid
        (False, reason)     if invalid
    """
    # 1. File must be present
    if file is None or file.filename == "":
        return False, "No file selected."

    # 2. Extension check
    if not allowed_file(file.filename):
        ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "none"
        return False, f"File type '.{ext}' is not allowed. Only CSV files are accepted."

    # 3. Dataset type must be known
    if dataset_type not in REQUIRED_COLUMNS:
        valid = ", ".join(REQUIRED_COLUMNS.keys())
        return False, f"Unknown dataset type '{dataset_type}'. Valid types: {valid}."

    # 4. File size check (read the stream position)
    file.stream.seek(0, os.SEEK_END)
    size = file.stream.tell()
    file.stream.seek(0)  # reset for subsequent reads
    max_mb = max_bytes // (1024 * 1024)
    if size > max_bytes:
        actual_mb = size / (1024 * 1024)
        return False, (
            f"File is {actual_mb:.1f} MB, which exceeds the {max_mb} MB limit."
        )

    logger.debug(
        "File '%s' passed basic validation (%.2f MB, type=%s)",
        file.filename, size / (1024 * 1024), dataset_type,
    )
    return True, ""


def validate_csv_columns(
    df_columns: list[str],
    dataset_type: str,
) -> tuple[bool, str]:
    """
    After reading the CSV into a DataFrame, verify required columns exist.

    Args:
        df_columns:   List of column names from the DataFrame.
        dataset_type: One of 'shipments', 'traffic', 'weather', 'gps'.

    Returns:
        (True, "")          if all required columns present
        (False, reason)     if any required column is missing
    """
    if dataset_type not in REQUIRED_COLUMNS:
        return False, f"Unknown dataset type: {dataset_type}"

    actual = set(c.strip().lower() for c in df_columns)
    required = set(c.lower() for c in REQUIRED_COLUMNS[dataset_type])
    missing = required - actual

    if missing:
        return False, (
            f"Missing required columns: {sorted(missing)}. "
            f"Check your CSV header row."
        )

    return True, ""


def sanitise_filename(filename: str) -> str:
    """
    Return a filesystem-safe version of the filename.
    Strips directory separators and replaces spaces with underscores.
    """
    name = Path(filename).name  # strip any path components
    name = name.replace(" ", "_")
    # Allow only alphanumerics, underscores, hyphens, dots
    safe = "".join(c for c in name if c.isalnum() or c in ("_", "-", "."))
    return safe or "upload"

