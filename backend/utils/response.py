"""
backend/utils/response.py
==========================
Standardised JSON response helpers for all API endpoints.

Every response follows the same envelope:
{
    "success": true | false,
    "data":    <payload or null>,
    "message": "<human-readable message>",
    "timestamp": "<ISO 8601>",
    "meta":    <optional pagination / metadata>
}
"""

from datetime import datetime, timezone
from flask import jsonify
from typing import Any


def _now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def success_response(
    data: Any = None,
    message: str = "OK",
    status_code: int = 200,
    meta: dict | None = None,
):
    """Return a successful JSON response."""
    payload = {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": _now_iso(),
    }
    if meta:
        payload["meta"] = meta
    return jsonify(payload), status_code


def error_response(
    message: str,
    error_type: str = "Error",
    status_code: int = 400,
    details: Any = None,
):
    """Return an error JSON response."""
    payload = {
        "success": False,
        "data": None,
        "error": error_type,
        "message": message,
        "timestamp": _now_iso(),
    }
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status_code


def paginated_response(
    data: list,
    page: int,
    per_page: int,
    total: int,
    message: str = "OK",
):
    """Return a paginated list response."""
    return success_response(
        data=data,
        message=message,
        meta={
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": max(1, -(-total // per_page)),  # ceiling division
        },
    )

