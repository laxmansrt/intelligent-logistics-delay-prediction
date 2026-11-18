"""
backend/services/spark_service.py
=================================
Service wrapper to trigger and track PySpark batch jobs.
"""

import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

from backend.config import Config
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class SparkService:
    """Manages execution of PySpark ETL and analytical aggregations."""

    def run_etl_job(self, input_file: str | Path | None = None) -> Dict[str, Any]:
        job_id = f"spark-etl-{uuid.uuid4().hex[:8]}"
        started_at = datetime.now(timezone.utc)

        self._record_job(job_id, "spark_etl", "running", started_at)

        try:
            from bigdata.spark.shipment_processor import process_shipments
            result = process_shipments(input_file)
            result["job_id"] = job_id
            self._record_job(job_id, "spark_etl", "completed", started_at, result)
            return result
        except Exception as exc:
            logger.exception("Spark ETL job %s failed", job_id)
            err_dict = {"success": False, "job_id": job_id, "error": str(exc)}
            self._record_job(job_id, "spark_etl", "failed", started_at, err_dict)
            return err_dict

    def run_route_analysis(self) -> Dict[str, Any]:
        job_id = f"spark-route-{uuid.uuid4().hex[:8]}"
        started_at = datetime.now(timezone.utc)
        self._record_job(job_id, "spark_route_analysis", "running", started_at)

        try:
            from bigdata.spark.route_analyzer import analyze_routes
            result = analyze_routes()
            result["job_id"] = job_id
            self._record_job(job_id, "spark_route_analysis", "completed", started_at, result)
            return result
        except Exception as exc:
            logger.exception("Spark route analysis job %s failed", job_id)
            err_dict = {"success": False, "job_id": job_id, "error": str(exc)}
            self._record_job(job_id, "spark_route_analysis", "failed", started_at, err_dict)
            return err_dict

    def run_delay_aggregation(self) -> Dict[str, Any]:
        job_id = f"spark-agg-{uuid.uuid4().hex[:8]}"
        started_at = datetime.now(timezone.utc)
        self._record_job(job_id, "spark_delay_aggregation", "running", started_at)

        try:
            from bigdata.spark.delay_aggregator import aggregate_delay_statistics
            result = aggregate_delay_statistics()
            result["job_id"] = job_id
            self._record_job(job_id, "spark_delay_aggregation", "completed", started_at, result)
            return result
        except Exception as exc:
            logger.exception("Spark delay aggregation job %s failed", job_id)
            err_dict = {"success": False, "job_id": job_id, "error": str(exc)}
            self._record_job(job_id, "spark_delay_aggregation", "failed", started_at, err_dict)
            return err_dict

    def _record_job(
        self,
        job_id: str,
        job_type: str,
        status: str,
        started_at: datetime,
        details: Dict[str, Any] | None = None,
    ):
        try:
            from backend.extensions import get_collection
            col = get_collection("processing_jobs")
            doc = {
                "job_id": job_id,
                "job_type": job_type,
                "status": status,
                "started_at": started_at.isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat() if status != "running" else None,
                "details": details or {},
            }
            col.update_one({"job_id": job_id}, {"$set": doc}, upsert=True)
        except Exception:
            pass


spark_service = SparkService()

