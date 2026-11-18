"""
backend/routes/health.py
=========================
Health-check and system-status endpoints.

GET /api/v1/health        → quick liveness probe
GET /api/v1/health/detail → full component status (DB, storage, Spark)

These endpoints are intentionally simple and do NOT require authentication.
They are used by:
  - The frontend dashboard to show system status
  - Load-balancers / monitors (in production)
  - Students to verify everything is running
"""

from flask import Blueprint
from backend.utils.response import success_response, error_response
from backend.utils.logger import get_logger
from backend.config import Config

logger = get_logger(__name__)

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def liveness():
    """
    Quick liveness check.
    Returns 200 if the Flask app is running.
    """
    return success_response(
        data={"status": "alive"},
        message="Logistics BDT API is running",
    )


@health_bp.route("/health/detail", methods=["GET"])
def detail():
    """
    Full component health check.
    Tests MongoDB connectivity and reports storage/Spark config.
    Returns 200 even if some components are unavailable,
    so the frontend can show a partial-degraded status rather than a 5xx.
    """
    components = {}

    # ── MongoDB ───────────────────────────────────────────
    try:
        from backend.extensions import mongo_client
        if mongo_client is not None:
            mongo_client.admin.command("ping")
            components["mongodb"] = {"status": "connected", "ok": True}
        else:
            components["mongodb"] = {"status": "not_initialised", "ok": False}
    except Exception as exc:
        components["mongodb"] = {"status": "error", "ok": False, "detail": str(exc)}

    # ── Storage mode ──────────────────────────────────────
    components["storage"] = {
        "mode": Config.STORAGE_MODE,
        "ok": True,
        "note": (
            "Using local filesystem (data/ directory)"
            if Config.STORAGE_MODE == "local"
            else "Using Apache HDFS"
        ),
    }

    # ── Spark ─────────────────────────────────────────────
    components["spark"] = {
        "mode": Config.SPARK_MODE,
        "master": Config.SPARK_MASTER,
        "ok": True,
        "note": (
            "PySpark local mode — runs on this machine"
            if Config.SPARK_MODE == "local"
            else "PySpark cluster mode"
        ),
    }

    # ── Overall status ────────────────────────────────────
    all_ok = all(v.get("ok", False) for v in components.values())
    overall = "healthy" if all_ok else "degraded"

    return success_response(
        data={
            "overall": overall,
            "components": components,
            "config": Config.summary(),
        },
        message=f"System is {overall}",
        status_code=200,  # always 200; frontend reads 'overall' field
    )

