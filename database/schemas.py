"""
database/schemas.py
====================
Reference document structures for all MongoDB collections.

This file is for DOCUMENTATION only — MongoDB does not enforce
schemas by default (that is intentional for schema-on-read flexibility).
Students can refer to these dicts to understand what fields
each collection contains.

BDT Concept:
    Schema-on-read: in a data lake / HDFS setup, raw data is stored
    without enforcing a schema at write time.  The schema is applied
    at query time by Spark or the application layer.  This allows
    different query engines to impose different schemas on the same data.
"""

# ── Shipment document ─────────────────────────────────────
SHIPMENT_SCHEMA = {
    "_id":                "ObjectId (auto)",
    "shipment_id":        "str — unique e.g. SHP-20230101-0001",
    "origin_city":        "str",
    "origin_state":       "str",
    "origin_lat":         "float",
    "origin_lon":         "float",
    "destination_city":   "str",
    "destination_state":  "str",
    "destination_lat":    "float",
    "destination_lon":    "float",
    "distance_km":        "float",
    "vehicle_type":       "str — Truck | Van | Mini-Truck | Rail | Air Cargo",
    "carrier":            "str",
    "weight_kg":          "float",
    "category":           "str — Electronics | Food | ...",
    "scheduled_pickup":   "ISO 8601 datetime string",
    "actual_pickup":      "ISO 8601 datetime string",
    "scheduled_delivery": "ISO 8601 datetime string",
    "actual_delivery":    "ISO 8601 datetime string",
    "is_delayed":         "int — 0=On-time, 1=Delayed  (ML TARGET)",
    "delay_minutes":      "float — 0 if not delayed",
    "delay_reason":       "str — 'No Delay' | 'Traffic Congestion' | ...",
    "status":             "str — Delivered | In Transit | Pending",
    "source_file":        "str — original upload filename",
    "data_source":        "str — SYNTHETIC or real dataset name",
    "ingested_at":        "ISO 8601",
    "_imported_at":       "ISO 8601",
}

# ── Traffic record ────────────────────────────────────────
TRAFFIC_SCHEMA = {
    "_id":              "ObjectId",
    "record_id":        "str — TRF-00001",
    "route_id":         "str — MUM-DEL-NH48",
    "timestamp":        "ISO 8601",
    "congestion_level": "int 1–5 (1=free flow, 5=gridlock)",
    "avg_speed_kmh":    "float",
    "incident_flag":    "int 0|1",
    "source_file":      "str",
    "ingested_at":      "ISO 8601",
}

# ── Weather record ────────────────────────────────────────
WEATHER_SCHEMA = {
    "_id":              "ObjectId",
    "record_id":        "str — WTH-00001",
    "city":             "str",
    "state":            "str",
    "timestamp":        "ISO 8601",
    "condition":        "str — Clear | Rain | Fog | Storm | Snow | Cloudy | Drizzle",
    "temperature_c":    "float",
    "wind_speed_kmh":   "float",
    "visibility_km":    "float",
    "precipitation_mm": "float",
    "source_file":      "str",
    "ingested_at":      "ISO 8601",
}

# ── GPS record ────────────────────────────────────────────
GPS_SCHEMA = {
    "_id":              "ObjectId",
    "record_id":        "str — GPS-SHP-…-01",
    "shipment_id":      "str — foreign key to shipments",
    "timestamp":        "ISO 8601",
    "latitude":         "float",
    "longitude":        "float",
    "speed_kmh":        "float",
    "heading_degrees":  "float 0–360",
    "source_file":      "str",
    "ingested_at":      "ISO 8601",
}

# ── Prediction result ─────────────────────────────────────
PREDICTION_SCHEMA = {
    "_id":                  "ObjectId",
    "shipment_id":          "str",
    "predicted_at":         "ISO 8601",
    "model_name":           "str — RandomForestClassifier",
    "model_version":        "str — rf_v1.0",
    "features_used":        "dict — feature values at prediction time",
    "is_delayed_predicted": "int 0|1",
    "delay_risk":           "str — Low | Medium | High",
    "confidence":           "float 0–1",
    "contributing_factors": "list[str]",
}

# ── Processing job ────────────────────────────────────────
JOB_SCHEMA = {
    "_id":               "ObjectId",
    "job_id":            "str — unique",
    "job_type":          "str — csv_ingestion | spark_etl | mapreduce | model_training",
    "dataset_type":      "str",
    "status":            "str — running | completed | failed",
    "records_processed": "int",
    "records_skipped":   "int",
    "storage_path":      "str",
    "errors":            "list[str]",
    "started_at":        "ISO 8601",
    "completed_at":      "ISO 8601",
}

# ── Model metrics ─────────────────────────────────────────
MODEL_METRICS_SCHEMA = {
    "_id":               "ObjectId",
    "model_name":        "str — RandomForestClassifier | LogisticRegression",
    "version":           "str",
    "trained_at":        "ISO 8601",
    "dataset_size":      "int",
    "train_size":        "int",
    "test_size":         "int",
    "accuracy":          "float — computed on test split (not hardcoded)",
    "precision":         "float",
    "recall":            "float",
    "f1_score":          "float",
    "confusion_matrix":  "list[list[int]]",
    "feature_importances": "dict — feature_name: importance_score",
    "hyperparameters":   "dict",
    "notes":             "str",
}

