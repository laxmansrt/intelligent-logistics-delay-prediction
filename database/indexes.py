"""
database/indexes.py
====================
Creates MongoDB indexes for all collections.

Run this once after first launch:
    python scripts/init_db.py

BDT Concept:
    Indexes in MongoDB (like in SQL databases) speed up queries
    dramatically. Without an index, MongoDB must scan every document
    (a "collection scan") — with an index, it jumps directly to the
    matching documents (a "covered query").

    For Big Data workloads, indexes are essential because we query
    millions of records by shipment_id, city, date range, etc.
"""

from pymongo import MongoClient, ASCENDING, DESCENDING, GEOSPHERE
from pymongo.errors import OperationFailure
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def create_all_indexes(db) -> dict[str, list[str]]:
    """
    Create all indexes on the given MongoDB database.

    Args:
        db: pymongo database handle

    Returns:
        Dict mapping collection name → list of created index names.
    """
    created = {}

    # ── shipments ─────────────────────────────────────────
    try:
        col = db["shipments"]
        col.create_index([("shipment_id", ASCENDING)], unique=True, name="idx_shipment_id_unique")
        col.create_index([("origin_city", ASCENDING), ("destination_city", ASCENDING)],
                         name="idx_route")
        col.create_index([("is_delayed", ASCENDING)], name="idx_is_delayed")
        col.create_index([("scheduled_delivery", DESCENDING)], name="idx_scheduled_delivery")
        col.create_index([("carrier", ASCENDING)], name="idx_carrier")
        col.create_index([("vehicle_type", ASCENDING)], name="idx_vehicle_type")
        col.create_index([("category", ASCENDING)], name="idx_category")
        col.create_index([("status", ASCENDING)], name="idx_status")
        col.create_index([("ingested_at", DESCENDING)], name="idx_ingested_at")
        created["shipments"] = [
            "idx_shipment_id_unique", "idx_route", "idx_is_delayed",
            "idx_scheduled_delivery", "idx_carrier", "idx_vehicle_type",
            "idx_category", "idx_status", "idx_ingested_at",
        ]
        logger.info("Created %d indexes on 'shipments'", len(created["shipments"]))
    except OperationFailure as exc:
        logger.warning("shipments index error: %s", exc)

    # ── traffic_records ───────────────────────────────────
    try:
        col = db["traffic_records"]
        col.create_index([("route_id", ASCENDING), ("timestamp", DESCENDING)],
                         name="idx_route_time")
        col.create_index([("congestion_level", ASCENDING)], name="idx_congestion")
        col.create_index([("incident_flag", ASCENDING)], name="idx_incident")
        created["traffic_records"] = ["idx_route_time", "idx_congestion", "idx_incident"]
        logger.info("Created indexes on 'traffic_records'")
    except OperationFailure as exc:
        logger.warning("traffic_records index error: %s", exc)

    # ── weather_records ───────────────────────────────────
    try:
        col = db["weather_records"]
        col.create_index([("city", ASCENDING), ("timestamp", DESCENDING)],
                         name="idx_city_time")
        col.create_index([("condition", ASCENDING)], name="idx_condition")
        created["weather_records"] = ["idx_city_time", "idx_condition"]
        logger.info("Created indexes on 'weather_records'")
    except OperationFailure as exc:
        logger.warning("weather_records index error: %s", exc)

    # ── gps_records ───────────────────────────────────────
    try:
        col = db["gps_records"]
        col.create_index([("shipment_id", ASCENDING), ("timestamp", ASCENDING)],
                         name="idx_shipment_time")
        # 2dsphere index enables geospatial queries (find records near a point)
        # Only possible if documents have a GeoJSON 'location' field.
        # col.create_index([("location", GEOSPHERE)], name="idx_location_geo")
        created["gps_records"] = ["idx_shipment_time"]
        logger.info("Created indexes on 'gps_records'")
    except OperationFailure as exc:
        logger.warning("gps_records index error: %s", exc)

    # ── prediction_results ────────────────────────────────
    try:
        col = db["prediction_results"]
        col.create_index([("shipment_id", ASCENDING)], name="idx_pred_shipment")
        col.create_index([("predicted_at", DESCENDING)], name="idx_pred_time")
        col.create_index([("delay_risk", ASCENDING)], name="idx_delay_risk")
        created["prediction_results"] = [
            "idx_pred_shipment", "idx_pred_time", "idx_delay_risk"
        ]
        logger.info("Created indexes on 'prediction_results'")
    except OperationFailure as exc:
        logger.warning("prediction_results index error: %s", exc)

    # ── processing_jobs ───────────────────────────────────
    try:
        col = db["processing_jobs"]
        col.create_index([("job_id", ASCENDING)], unique=True, name="idx_job_id")
        col.create_index([("job_type", ASCENDING), ("status", ASCENDING)],
                         name="idx_job_type_status")
        col.create_index([("started_at", DESCENDING)], name="idx_job_started")
        created["processing_jobs"] = ["idx_job_id", "idx_job_type_status", "idx_job_started"]
        logger.info("Created indexes on 'processing_jobs'")
    except OperationFailure as exc:
        logger.warning("processing_jobs index error: %s", exc)

    # ── model_metrics ─────────────────────────────────────
    try:
        col = db["model_metrics"]
        col.create_index([("model_name", ASCENDING), ("version", ASCENDING)],
                         name="idx_model_version")
        col.create_index([("trained_at", DESCENDING)], name="idx_trained_at")
        created["model_metrics"] = ["idx_model_version", "idx_trained_at"]
        logger.info("Created indexes on 'model_metrics'")
    except OperationFailure as exc:
        logger.warning("model_metrics index error: %s", exc)

    return created

