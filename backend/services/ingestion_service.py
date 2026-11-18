"""
backend/services/ingestion_service.py
=======================================
CSV ingestion pipeline — reads uploaded files, validates them,
cleans the data, writes records to MongoDB, and saves the file
to storage.

Pipeline flow:
    upload → validate file → save raw → read CSV → validate columns
           → clean / normalise → insert into MongoDB → return report

BDT Concept:
    This is the data ingestion stage of the pipeline — equivalent
    to the "data collection" layer in a Hadoop ecosystem where raw
    data lands in HDFS before being processed by Spark or MapReduce.
"""

import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

import pandas as pd

from backend.utils.validators import validate_csv_columns, sanitise_filename
from backend.utils.logger import get_logger
from backend.services.storage_service import storage

logger = get_logger(__name__)

# Column name normalisations: lowercase + strip spaces
# Maps common alternate column names to our canonical names
COLUMN_ALIASES = {
    "shipments": {
        "id":                "shipment_id",
        "ship_id":           "shipment_id",
        "from_city":         "origin_city",
        "to_city":           "destination_city",
        "delay":             "is_delayed",
        "delayed":           "is_delayed",
        "delay_flag":        "is_delayed",
    },
    "traffic": {},
    "weather": {
        "weather_condition": "condition",
        "temp":              "temperature_c",
        "temperature":       "temperature_c",
    },
    "gps": {
        "lat":               "latitude",
        "lon":               "longitude",
        "lng":               "longitude",
        "speed":             "speed_kmh",
    },
}


class IngestionService:
    """
    Handles the full CSV → MongoDB ingestion pipeline.
    Each dataset type has its own cleaning method.
    """

    def __init__(self):
        # Lazy import to avoid circular dep issues at module load
        pass

    def ingest_file(
        self,
        file_path: str | Path,
        dataset_type: str,
        original_filename: str,
        job_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Full ingestion pipeline for one CSV file.

        Args:
            file_path:         Path to the uploaded CSV on disk.
            dataset_type:      'shipments' | 'traffic' | 'weather' | 'gps'
            original_filename: Original filename for logging.
            job_id:            Optional job ID for tracking in MongoDB.

        Returns:
            Report dict:
            {
                "success": bool,
                "job_id": str,
                "dataset_type": str,
                "records_read": int,
                "records_inserted": int,
                "records_skipped": int,
                "errors": [str],
                "storage_path": str,
                "duration_seconds": float,
            }
        """
        job_id = job_id or str(uuid.uuid4())[:8]
        started_at = datetime.now(timezone.utc)
        report = {
            "success": False,
            "job_id": job_id,
            "dataset_type": dataset_type,
            "original_filename": original_filename,
            "records_read": 0,
            "records_inserted": 0,
            "records_skipped": 0,
            "errors": [],
            "storage_path": "",
            "started_at": started_at.isoformat(),
            "duration_seconds": 0.0,
        }

        try:
            logger.info("[%s] Ingesting %s (%s)", job_id, original_filename, dataset_type)

            # ── Step 1: Save raw file to storage ──────────
            safe_name = sanitise_filename(original_filename)
            storage_path = storage.save_file(file_path, dataset_type, safe_name)
            report["storage_path"] = storage_path

            # ── Step 2: Read CSV into DataFrame ───────────
            df = pd.read_csv(file_path, low_memory=False)
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
            report["records_read"] = len(df)
            logger.info("[%s] Read %d rows", job_id, len(df))

            # ── Step 3: Apply column aliases ──────────────
            aliases = COLUMN_ALIASES.get(dataset_type, {})
            df = df.rename(columns=aliases)

            # ── Step 4: Validate required columns ─────────
            ok, msg = validate_csv_columns(list(df.columns), dataset_type)
            if not ok:
                report["errors"].append(msg)
                logger.warning("[%s] Column validation failed: %s", job_id, msg)
                return self._finalise(report, started_at)

            # ── Step 5: Clean / normalise ─────────────────
            df, skipped, clean_errors = self._clean(df, dataset_type)
            report["records_skipped"] = skipped
            report["errors"].extend(clean_errors)

            # ── Step 6: Insert into MongoDB ────────────────
            inserted = self._insert_to_mongo(df, dataset_type, original_filename)
            report["records_inserted"] = inserted

            # ── Step 7: Record the job in MongoDB ──────────
            self._record_job(report, dataset_type)

            report["success"] = True
            logger.info(
                "[%s] Done — inserted %d, skipped %d",
                job_id, inserted, skipped,
            )

        except pd.errors.EmptyDataError:
            report["errors"].append("The uploaded CSV file is empty.")
        except pd.errors.ParserError as exc:
            report["errors"].append(f"CSV parse error: {exc}")
        except Exception as exc:
            report["errors"].append(f"Unexpected error: {exc}")
            logger.exception("[%s] Ingestion failed", job_id)

        return self._finalise(report, started_at)

    # ── Cleaning ───────────────────────────────────────────

    def _clean(
        self,
        df: pd.DataFrame,
        dataset_type: str,
    ) -> tuple[pd.DataFrame, int, list[str]]:
        """
        Clean and normalise a DataFrame.
        Returns (cleaned_df, n_skipped, error_messages).
        """
        original_len = len(df)
        errors = []

        # Drop fully duplicate rows
        df = df.drop_duplicates()

        # Type-specific cleaning
        cleaner = {
            "shipments": self._clean_shipments,
            "traffic":   self._clean_traffic,
            "weather":   self._clean_weather,
            "gps":       self._clean_gps,
        }.get(dataset_type)

        if cleaner:
            df, type_errors = cleaner(df)
            errors.extend(type_errors)

        skipped = original_len - len(df)
        return df, skipped, errors

    def _clean_shipments(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        errors = []

        # Coerce is_delayed to int (handle True/False/Yes/No strings)
        if "is_delayed" in df.columns:
            df["is_delayed"] = (
                df["is_delayed"]
                .astype(str)
                .str.strip()
                .str.lower()
                .map({"1": 1, "0": 0, "true": 1, "false": 0,
                      "yes": 1, "no": 0, "y": 1, "n": 0})
            )
            invalid = df["is_delayed"].isna().sum()
            if invalid:
                errors.append(
                    f"{invalid} rows have unrecognised 'is_delayed' values and will be dropped."
                )
            df = df.dropna(subset=["is_delayed"])
            df["is_delayed"] = df["is_delayed"].astype(int)

        # Drop rows missing shipment_id
        if "shipment_id" in df.columns:
            before = len(df)
            df = df.dropna(subset=["shipment_id"])
            if len(df) < before:
                errors.append(f"{before - len(df)} rows dropped: missing shipment_id.")

        # Coerce numeric columns
        for col in ["distance_km", "weight_kg", "delay_minutes"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Strip whitespace from string cols
        for col in ["origin_city", "destination_city", "vehicle_type",
                    "carrier", "category", "status"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        # Add ingestion metadata
        df["ingested_at"] = datetime.now(timezone.utc).isoformat()
        return df, errors

    def _clean_traffic(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        errors = []
        if "congestion_level" in df.columns:
            df["congestion_level"] = pd.to_numeric(df["congestion_level"], errors="coerce")
            df = df.dropna(subset=["congestion_level"])
            df["congestion_level"] = df["congestion_level"].clip(1, 5).astype(int)
        if "avg_speed_kmh" in df.columns:
            df["avg_speed_kmh"] = pd.to_numeric(df["avg_speed_kmh"], errors="coerce")
        df["ingested_at"] = datetime.now(timezone.utc).isoformat()
        return df, errors

    def _clean_weather(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        errors = []
        for col in ["temperature_c", "wind_speed_kmh", "visibility_km", "precipitation_mm"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        if "condition" in df.columns:
            df["condition"] = df["condition"].astype(str).str.strip().str.title()
        df["ingested_at"] = datetime.now(timezone.utc).isoformat()
        return df, errors

    def _clean_gps(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        errors = []
        for col in ["latitude", "longitude", "speed_kmh"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        # Drop GPS rows with invalid coordinates
        before = len(df)
        df = df.dropna(subset=["latitude", "longitude"])
        df = df[df["latitude"].between(-90, 90) & df["longitude"].between(-180, 180)]
        dropped = before - len(df)
        if dropped:
            errors.append(f"{dropped} GPS rows dropped: invalid coordinates.")
        df["ingested_at"] = datetime.now(timezone.utc).isoformat()
        return df, errors

    # ── MongoDB ────────────────────────────────────────────

    def _insert_to_mongo(
        self,
        df: pd.DataFrame,
        dataset_type: str,
        source_file: str,
    ) -> int:
        """
        Insert DataFrame rows as MongoDB documents.
        Returns number of records inserted.
        Skips gracefully if MongoDB is unavailable.
        """
        collection_map = {
            "shipments": "shipments",
            "traffic":   "traffic_records",
            "weather":   "weather_records",
            "gps":       "gps_records",
        }
        collection_name = collection_map.get(dataset_type)
        if not collection_name:
            return 0

        try:
            from backend.extensions import get_collection
            collection = get_collection(collection_name)

            records = df.to_dict(orient="records")
            # Add source metadata to each document
            for rec in records:
                rec["source_file"] = source_file
                rec["_imported_at"] = datetime.now(timezone.utc).isoformat()

            if records:
                result = collection.insert_many(records, ordered=False)
                return len(result.inserted_ids)
            return 0

        except RuntimeError:
            logger.warning(
                "MongoDB not available — records NOT persisted to database."
                " Start MongoDB to enable persistence."
            )
            return 0
        except Exception as exc:
            logger.error("MongoDB insert error: %s", exc)
            return 0

    def _record_job(self, report: dict, dataset_type: str) -> None:
        """Save ingestion job record to processing_jobs collection."""
        try:
            from backend.extensions import get_collection
            jobs = get_collection("processing_jobs")
            jobs.insert_one({
                "job_id":            report["job_id"],
                "job_type":          "csv_ingestion",
                "dataset_type":      dataset_type,
                "status":            "completed" if report["success"] else "failed",
                "records_processed": report["records_inserted"],
                "records_skipped":   report["records_skipped"],
                "storage_path":      report["storage_path"],
                "errors":            report["errors"],
                "started_at":        report["started_at"],
                "completed_at":      datetime.now(timezone.utc).isoformat(),
            })
        except Exception:
            pass  # Job logging is non-critical

    @staticmethod
    def _finalise(report: dict, started_at: datetime) -> dict:
        """Add duration and return the final report."""
        elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
        report["duration_seconds"] = round(elapsed, 3)
        return report


# Module-level singleton
ingestion = IngestionService()
