"""
backend/routes/shipments.py
===========================
API endpoints for shipment queries, filtering, and summary metrics.
"""

from pathlib import Path
from flask import Blueprint, request
import pandas as pd

from backend.config import Config
from backend.utils.response import success_response, error_response, paginated_response
from backend.utils.logger import get_logger

logger = get_logger(__name__)
shipments_bp = Blueprint("shipments", __name__)


def _load_shipments_df() -> pd.DataFrame:
    """Helper to load shipments from MongoDB or fallback to local CSV."""
    try:
        from backend.extensions import get_collection
        col = get_collection("shipments")
        docs = list(col.find({}, {"_id": 0}))
        if docs:
            return pd.DataFrame(docs)
    except Exception:
        pass

    # Local fallback
    sample_path = Config.DATA_DIR / "sample" / "sample_shipments.csv"
    if sample_path.exists():
        return pd.read_csv(sample_path)
    return pd.DataFrame()


@shipments_bp.route("/shipments", methods=["GET"])
def get_shipments():
    """Paginated list of shipments with multi-attribute filtering."""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 15))
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    is_delayed = request.args.get("is_delayed")
    carrier = request.args.get("carrier")
    search = request.args.get("search")

    df = _load_shipments_df()
    if df.empty:
        return paginated_response([], page=page, per_page=per_page, total=0)

    # Apply filters
    if origin:
        df = df[df["origin_city"].astype(str).str.lower() == origin.lower()]
    if destination:
        df = df[df["destination_city"].astype(str).str.lower() == destination.lower()]
    if carrier:
        df = df[df["carrier"].astype(str).str.lower() == carrier.lower()]
    if is_delayed is not None and is_delayed != "":
        delayed_val = int(is_delayed)
        df = df[df["is_delayed"] == delayed_val]
    if search:
        search_lower = search.lower()
        df = df[
            df["shipment_id"].astype(str).str.lower().str.contains(search_lower) |
            df["origin_city"].astype(str).str.lower().str.contains(search_lower) |
            df["destination_city"].astype(str).str.lower().str.contains(search_lower)
        ]

    total = len(df)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_records = df.iloc[start_idx:end_idx].to_dict(orient="records")

    return paginated_response(page_records, page=page, per_page=per_page, total=total)


@shipments_bp.route("/shipments/<shipment_id>", methods=["GET"])
def get_shipment_by_id(shipment_id: str):
    """Retrieve details of a single shipment by its ID."""
    df = _load_shipments_df()
    if df.empty:
        return error_response(f"Shipment '{shipment_id}' not found.", status_code=404)

    match = df[df["shipment_id"] == shipment_id]
    if match.empty:
        return error_response(f"Shipment '{shipment_id}' not found.", status_code=404)

    return success_response(data=match.iloc[0].to_dict())


@shipments_bp.route("/shipments/stats/summary", methods=["GET"])
def get_kpi_summary():
    """Calculate and return real computed KPI metrics from shipment data."""
    df = _load_shipments_df()
    if df.empty:
        return success_response(data={
            "total_shipments": 0, "on_time_shipments": 0, "delayed_shipments": 0,
            "delay_percentage": 0.0, "avg_delay_minutes": 0.0,
        })

    total = len(df)
    delayed = int((df["is_delayed"] == 1).sum())
    on_time = total - delayed
    delay_rate = round((delayed / total * 100.0), 2) if total > 0 else 0.0

    avg_delay_mins = 0.0
    if "delay_minutes" in df.columns:
        delayed_rows = df[df["is_delayed"] == 1]
        if not delayed_rows.empty:
            avg_delay_mins = round(float(delayed_rows["delay_minutes"].mean()), 1)

    return success_response(data={
        "total_shipments": total,
        "on_time_shipments": on_time,
        "delayed_shipments": delayed,
        "delay_percentage": delay_rate,
        "avg_delay_minutes": avg_delay_mins,
    })

