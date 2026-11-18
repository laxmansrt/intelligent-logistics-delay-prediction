"""
backend/routes/upload.py
=========================
API endpoints for uploading and ingesting CSV datasets.

Endpoints:
    POST /api/v1/upload/<dataset_type>   Upload + ingest a CSV
    GET  /api/v1/upload/status/<job_id>  Check ingestion job status
    GET  /api/v1/upload/files            List all uploaded files
    POST /api/v1/upload/load-sample      Load bundled sample data

Supported dataset_type values: shipments | traffic | weather | gps
"""

import tempfile
from pathlib import Path
from flask import Blueprint, request
from backend.utils.response import success_response, error_response
from backend.utils.validators import validate_upload, sanitise_filename
from backend.utils.logger import get_logger
from backend.config import Config

logger = get_logger(__name__)
upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload/<dataset_type>", methods=["POST"])
def upload_dataset(dataset_type: str):
    """
    Upload a CSV file and run the full ingestion pipeline.

    Form-data fields:
        file  — the CSV file (required)

    Returns the ingestion report including records inserted,
    records skipped, errors, and storage path.
    """
    valid_types = {"shipments", "traffic", "weather", "gps"}
    if dataset_type not in valid_types:
        return error_response(
            f"Unknown dataset type '{dataset_type}'. "
            f"Valid types: {', '.join(sorted(valid_types))}",
            error_type="ValidationError",
            status_code=400,
        )

    if "file" not in request.files:
        return error_response(
            "No file part in the request. "
            "Send the file as form-data with key 'file'.",
            error_type="ValidationError",
            status_code=400,
        )

    file = request.files["file"]
    max_bytes = Config.MAX_UPLOAD_MB * 1024 * 1024

    # Validate file (extension, size, type)
    ok, reason = validate_upload(file, dataset_type, max_bytes)
    if not ok:
        return error_response(reason, error_type="ValidationError", status_code=400)

    # Save to a secure temp file (avoids path traversal)
    safe_name = sanitise_filename(file.filename)
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".csv",
        prefix=f"{dataset_type}_",
    ) as tmp:
        file.save(tmp.name)
        tmp_path = Path(tmp.name)

    try:
        from backend.services.ingestion_service import ingestion
        report = ingestion.ingest_file(
            file_path=tmp_path,
            dataset_type=dataset_type,
            original_filename=safe_name,
        )
    finally:
        # Always clean up the temp file
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass

    if report["success"]:
        return success_response(
            data=report,
            message=(
                f"Ingestion complete. "
                f"{report['records_inserted']} records inserted, "
                f"{report['records_skipped']} skipped."
            ),
            status_code=201,
        )
    else:
        return error_response(
            message="Ingestion failed. See 'details' for errors.",
            error_type="IngestionError",
            status_code=422,
            details=report,
        )


@upload_bp.route("/upload/status/<job_id>", methods=["GET"])
def upload_status(job_id: str):
    """
    Retrieve the status of an ingestion job by job_id.
    """
    try:
        from backend.extensions import get_collection
        jobs = get_collection("processing_jobs")
        job = jobs.find_one(
            {"job_id": job_id},
            {"_id": 0}
        )
        if not job:
            return error_response(
                f"Job '{job_id}' not found.",
                error_type="NotFound",
                status_code=404,
            )
        return success_response(data=job)
    except RuntimeError:
        return error_response(
            "Database unavailable. Start MongoDB to track jobs.",
            error_type="DatabaseError",
            status_code=503,
        )


@upload_bp.route("/upload/files", methods=["GET"])
def list_uploaded_files():
    """
    List all uploaded files in the raw storage directory.
    Optional query param: ?type=shipments
    """
    dataset_type = request.args.get("type", "")
    subdir = f"raw/{dataset_type}" if dataset_type else "raw"

    from backend.services.storage_service import storage
    files = storage.list_files(subdir)

    return success_response(
        data={"files": files, "storage": storage.get_storage_info()},
        message=f"{len(files)} file(s) found",
    )


@upload_bp.route("/upload/load-sample", methods=["POST"])
def load_sample_data():
    """
    Ingest all bundled SYNTHETIC sample CSVs from data/sample/.

    ⚠️  Clearly disclosed: these are SYNTHETIC datasets.
    This endpoint is for quick demonstration only.
    """
    sample_dir = Config.SAMPLE_DIR
    sample_files = {
        "shipments": "sample_shipments.csv",
        "traffic":   "sample_traffic.csv",
        "weather":   "sample_weather.csv",
        "gps":       "sample_gps.csv",
    }

    # Check sample files exist — generate them if not
    missing = [
        name for name in sample_files.values()
        if not (sample_dir / name).exists()
    ]
    if missing:
        logger.info("Sample files not found, generating them now...")
        try:
            import subprocess, sys
            script = Config.DATA_DIR.parent / "scripts" / "generate_sample_data.py"
            subprocess.run(
                [sys.executable, str(script)],
                check=True,
                capture_output=True,
                timeout=120,
            )
        except Exception as exc:
            return error_response(
                f"Could not generate sample data: {exc}. "
                "Run: python scripts/generate_sample_data.py",
                error_type="GenerationError",
                status_code=500,
            )

    from backend.services.ingestion_service import ingestion
    results = {}
    for dataset_type, filename in sample_files.items():
        path = sample_dir / filename
        if path.exists():
            report = ingestion.ingest_file(
                file_path=path,
                dataset_type=dataset_type,
                original_filename=filename,
            )
            results[dataset_type] = {
                "success":           report["success"],
                "records_inserted":  report["records_inserted"],
                "records_skipped":   report["records_skipped"],
                "errors":            report["errors"],
                "data_disclosure":   "SYNTHETIC data — not real logistics records",
            }
        else:
            results[dataset_type] = {"success": False, "errors": [f"{filename} not found"]}

    total_inserted = sum(r.get("records_inserted", 0) for r in results.values())
    return success_response(
        data={
            "results": results,
            "total_inserted": total_inserted,
            "data_disclosure": (
                "⚠️ All sample data is SYNTHETICALLY GENERATED. "
                "It does not represent real shipment records."
            ),
        },
        message=f"Sample data loaded. {total_inserted} total records inserted.",
        status_code=201,
    )

