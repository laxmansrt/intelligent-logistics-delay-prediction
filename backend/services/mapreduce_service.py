"""
backend/services/mapreduce_service.py
=====================================
Service wrapper to trigger and track MapReduce batch jobs.
"""

import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

from backend.config import Config
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class MapReduceService:
    """Manages execution of MapReduce streaming batch jobs."""

    def run_job(self, input_csv_path: str | Path | None = None) -> Dict[str, Any]:
        job_id = f"mr-batch-{uuid.uuid4().hex[:8]}"
        started_at = datetime.now(timezone.utc)

        if input_csv_path is None:
            input_csv_path = Config.DATA_DIR / "sample" / "sample_shipments.csv"

        input_path = Path(input_csv_path)
        if not input_path.exists():
            return {
                "success": False,
                "job_id": job_id,
                "error": f"Input file not found: {input_path}",
            }

        self._record_job(job_id, "mapreduce_batch", "running", started_at)

        try:
            from bigdata.mapreduce.run_mapreduce import run_mapreduce_job
            result = run_mapreduce_job(input_path)
            result["job_id"] = job_id
            self._record_job(job_id, "mapreduce_batch", "completed" if result["success"] else "failed", started_at, result)
            return result
        except Exception as exc:
            logger.exception("MapReduce job %s failed", job_id)
            err_dict = {"success": False, "job_id": job_id, "error": str(exc)}
            self._record_job(job_id, "mapreduce_batch", "failed", started_at, err_dict)
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


mapreduce_service = MapReduceService()

