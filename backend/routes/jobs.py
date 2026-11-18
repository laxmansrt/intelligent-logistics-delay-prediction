"""
backend/routes/jobs.py
======================
API Endpoints to trigger and monitor distributed Big Data jobs (Spark & MapReduce).
"""

from flask import Blueprint, request
from backend.utils.response import success_response, error_response
from backend.utils.logger import get_logger
from backend.services.spark_service import spark_service
from backend.services.mapreduce_service import mapreduce_service

logger = get_logger(__name__)
jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("/jobs/spark/run", methods=["POST"])
def run_spark_etl():
    """Trigger the PySpark ETL and deduplication pipeline."""
    result = spark_service.run_etl_job()
    if result.get("success"):
        return success_response(data=result, message="Spark ETL pipeline executed successfully.")
    return error_response(f"Spark ETL failed: {result.get('error')}", status_code=500)


@jobs_bp.route("/jobs/spark/routes", methods=["POST"])
def run_spark_routes():
    """Trigger the PySpark route risk analysis job."""
    result = spark_service.run_route_analysis()
    if result.get("success"):
        return success_response(data=result, message="Spark route analysis completed.")
    return error_response(f"Spark route analysis failed: {result.get('error')}", status_code=500)


@jobs_bp.route("/jobs/mapreduce/run", methods=["POST"])
def run_mapreduce():
    """Trigger the MapReduce batch analytics job."""
    result = mapreduce_service.run_job()
    if result.get("success"):
        return success_response(data=result, message="MapReduce batch job completed successfully.")
    return error_response(f"MapReduce job failed: {result.get('error')}", status_code=500)


@jobs_bp.route("/jobs", methods=["GET"])
def list_jobs():
    """List history of data processing jobs."""
    try:
        from backend.extensions import get_collection
        col = get_collection("processing_jobs")
        jobs = list(col.find({}, {"_id": 0}).sort("started_at", -1).limit(50))
        return success_response(data={"jobs": jobs, "total": len(jobs)})
    except Exception:
        return success_response(data={"jobs": [], "total": 0, "note": "Database offline"})


@jobs_bp.route("/jobs/<job_id>", methods=["GET"])
def get_job(job_id: str):
    """Retrieve execution log and status for a single job."""
    try:
        from backend.extensions import get_collection
        col = get_collection("processing_jobs")
        job = col.find_one({"job_id": job_id}, {"_id": 0})
        if not job:
            return error_response(f"Job '{job_id}' not found.", status_code=404)
        return success_response(data=job)
    except Exception:
        return error_response("Database offline", status_code=503)

