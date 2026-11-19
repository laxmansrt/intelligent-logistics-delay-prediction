"""
backend/routes/hive.py
======================
API Endpoints for Apache Hive Big Data Querying, Classification Analytics, and Warehouse Management.

Official Title Alignment:
    "Big Data Classification and Prediction for Transportation and Logistics using Apache Hive"
"""

from flask import Blueprint, request
from backend.utils.response import success_response, error_response
from backend.utils.logger import get_logger
from backend.services.hive_service import hive_service, HIVE_QUERIES_DIR

logger = get_logger(__name__)
hive_bp = Blueprint("hive", __name__)


@hive_bp.route("/hive/status", methods=["GET"])
def hive_status():
    """Returns Apache Hive connection mode, warehouse directory, and metastore status."""
    status = hive_service.get_hive_status()
    return success_response(data=status, message="Hive status retrieved successfully.")


@hive_bp.route("/hive/init", methods=["POST"])
def init_hive_warehouse():
    """Triggers DDL creation and loading of partitioned ORC tables in Apache Hive."""
    try:
        report = hive_service.initialize_hive_schema()
        return success_response(data=report, message="Apache Hive database and tables initialized.")
    except Exception as exc:
        logger.exception("Hive initialization endpoint failed")
        return error_response(f"Hive initialization failed: {exc}", status_code=500)


@hive_bp.route("/hive/query/<query_name>", methods=["GET"])
def execute_named_hive_query(query_name: str):
    """
    Executes one of the 7 official HiveQL analytics queries:
    - total_shipments
    - ontime_vs_delayed
    - delay_percentage
    - avg_delivery_duration
    - routes_highest_delays
    - transportation_mode_analysis
    - monthly_shipment_trends
    """
    try:
        result = hive_service.run_named_query(query_name)
        if result.get("success"):
            return success_response(data=result, message=f"HiveQL query '{query_name}' executed successfully.")
        return error_response(f"HiveQL query failed: {result.get('error')}", status_code=500)
    except Exception as exc:
        return error_response(f"Error executing Hive query '{query_name}': {exc}", status_code=400)


@hive_bp.route("/hive/query", methods=["POST"])
def execute_custom_hiveql():
    """Executes arbitrary HiveQL query entered by the user in the interactive console."""
    data = request.get_json()
    if not data or "query" not in data:
        return error_response("Request body must include 'query' string parameter.", status_code=400)

    query_str = data["query"]
    result = hive_service.execute_hiveql(query_str)
    if result.get("success"):
        return success_response(data=result, message="HiveQL statement executed.")
    return error_response(f"HiveQL error: {result.get('error')}", status_code=400)


@hive_bp.route("/hive/scripts", methods=["GET"])
def list_hive_scripts():
    """Lists the official HiveQL script files with their SQL definitions."""
    scripts = []
    if HIVE_QUERIES_DIR.exists():
        for f in sorted(HIVE_QUERIES_DIR.glob("*.hql")):
            content = f.read_text(encoding="utf-8")
            scripts.append({
                "filename": f.name,
                "title": f.name.replace(".hql", "").replace("_", " ").title(),
                "query": content,
            })
    return success_response(data={"scripts": scripts, "count": len(scripts)})
