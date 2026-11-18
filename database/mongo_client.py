"""
database/mongo_client.py
=========================
MongoDB connection helper and collection accessor utilities.

BDT Concept:
    MongoDB is a NoSQL document database — ideal for logistics data
    where each shipment, weather record, or GPS ping has a flexible
    schema that evolves over time.  Unlike SQL, we don't need to
    define a rigid table structure upfront.

Collections used in this project:
    shipments          — core shipment records
    traffic_records    — traffic conditions per route/time
    weather_records    — weather observations per city/time
    gps_records        — GPS waypoints per shipment
    prediction_results — ML delay predictions
    processing_jobs    — Spark/MapReduce/ingestion job logs
    model_metrics      — ML model training evaluation results
"""

from pymongo import MongoClient, ASCENDING, DESCENDING, GEOSPHERE
from pymongo.errors import ConnectionFailure, OperationFailure
from backend.config import Config
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Collection name constants — use these everywhere to avoid typos
COL_SHIPMENTS    = "shipments"
COL_TRAFFIC      = "traffic_records"
COL_WEATHER      = "weather_records"
COL_GPS          = "gps_records"
COL_PREDICTIONS  = "prediction_results"
COL_JOBS         = "processing_jobs"
COL_METRICS      = "model_metrics"

ALL_COLLECTIONS = [
    COL_SHIPMENTS, COL_TRAFFIC, COL_WEATHER, COL_GPS,
    COL_PREDICTIONS, COL_JOBS, COL_METRICS,
]


def get_mongo_client() -> MongoClient | None:
    """
    Create and return a MongoClient.
    Returns None (with a warning) if the connection fails,
    so callers can degrade gracefully.
    """
    try:
        client = MongoClient(
            Config.MONGO_URI,
            serverSelectionTimeoutMS=3000,
        )
        client.admin.command("ping")
        return client
    except (ConnectionFailure, Exception) as exc:
        logger.warning("MongoDB unavailable: %s", exc)
        return None


def get_database():
    """Return the logistics database handle, or None if unavailable."""
    client = get_mongo_client()
    if client is None:
        return None
    return client[Config.MONGO_DB_NAME]


def get_collection_stats() -> dict:
    """
    Return document counts for all collections.
    Used by the dashboard overview endpoint.
    """
    db = get_database()
    if db is None:
        return {col: {"count": 0, "available": False} for col in ALL_COLLECTIONS}

    stats = {}
    for col_name in ALL_COLLECTIONS:
        try:
            count = db[col_name].estimated_document_count()
            stats[col_name] = {"count": count, "available": True}
        except Exception as exc:
            stats[col_name] = {"count": 0, "available": False, "error": str(exc)}
    return stats

