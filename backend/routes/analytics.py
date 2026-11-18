"""
backend/routes/analytics.py
===========================
API endpoints providing aggregated analytical distributions for Chart.js.
"""

import json
from pathlib import Path
from flask import Blueprint
import pandas as pd

from backend.config import Config
from backend.utils.response import success_response, error_response
from backend.routes.shipments import _load_shipments_df

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics/delay-reasons", methods=["GET"])
def get_delay_reasons():
    """Returns frequency distribution of reasons for delayed shipments."""
    df = _load_shipments_df()
    if df.empty or "delay_reason" not in df.columns:
        return success_response(data={"labels": [], "counts": []})

    delayed_df = df[df["is_delayed"] == 1]
    counts = delayed_df["delay_reason"].value_counts().to_dict()

    return success_response(data={
        "labels": list(counts.keys()),
        "counts": list(counts.values()),
    })


@analytics_bp.route("/analytics/route-performance", methods=["GET"])
def get_route_performance():
    """Returns route bottleneck statistics."""
    analytics_file = Config.DATA_DIR / "analytics" / "route_performance.csv"
    if analytics_file.exists():
        routes_df = pd.read_csv(analytics_file)
    else:
        # Fallback compute on the fly
        df = _load_shipments_df()
        if df.empty:
            return success_response(data={"routes": []})
        routes_df = (
            df.groupby(["origin_city", "destination_city"])
            .agg(
                total_shipments=("shipment_id", "count"),
                delayed_shipments=("is_delayed", "sum"),
                avg_distance_km=("distance_km", "mean"),
            )
            .reset_index()
        )
        routes_df["delay_rate_pct"] = (routes_df["delayed_shipments"] / routes_df["total_shipments"]) * 100.0
        routes_df = routes_df.sort_values(by="delay_rate_pct", ascending=False)

    records = routes_df.head(20).to_dict(orient="records")
    return success_response(data={"routes": records})


@analytics_bp.route("/analytics/carrier-performance", methods=["GET"])
def get_carrier_performance():
    """Returns carrier delivery performance comparison."""
    df = _load_shipments_df()
    if df.empty or "carrier" not in df.columns:
        return success_response(data={"carriers": []})

    carrier_stats = (
        df.groupby("carrier")
        .agg(
            total=("shipment_id", "count"),
            delayed=("is_delayed", "sum"),
        )
        .reset_index()
    )
    carrier_stats["delay_rate"] = (carrier_stats["delayed"] / carrier_stats["total"]) * 100.0
    carrier_stats = carrier_stats.sort_values(by="delay_rate", ascending=False)

    return success_response(data={
        "labels": carrier_stats["carrier"].tolist(),
        "delay_rates": carrier_stats["delay_rate"].round(1).tolist(),
        "totals": carrier_stats["total"].tolist(),
    })


@analytics_bp.route("/analytics/vehicle-performance", methods=["GET"])
def get_vehicle_performance():
    """Returns delay percentage comparison across vehicle types."""
    df = _load_shipments_df()
    if df.empty or "vehicle_type" not in df.columns:
        return success_response(data={"labels": [], "delay_rates": []})

    vehicle_stats = (
        df.groupby("vehicle_type")
        .agg(
            total=("shipment_id", "count"),
            delayed=("is_delayed", "sum"),
        )
        .reset_index()
    )
    vehicle_stats["delay_rate"] = (vehicle_stats["delayed"] / vehicle_stats["total"]) * 100.0

    return success_response(data={
        "labels": vehicle_stats["vehicle_type"].tolist(),
        "delay_rates": vehicle_stats["delay_rate"].round(1).tolist(),
        "totals": vehicle_stats["total"].tolist(),
    })


@analytics_bp.route("/analytics/model-metrics", methods=["GET"])
def get_model_metrics():
    """Returns real evaluated metrics for Random Forest and baseline models."""
    metrics_file = Config.DATA_DIR / "models" / "evaluation_metrics.json"
    if metrics_file.exists():
        with open(metrics_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return success_response(data=data)

    return success_response(
        data=None,
        message="Model has not been trained yet. Trigger training via POST /api/v1/model/train",
    )

