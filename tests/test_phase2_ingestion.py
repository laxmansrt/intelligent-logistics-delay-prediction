"""
tests/test_phase2_ingestion.py
================================
Phase 2 tests: Sample data generation, storage service,
ingestion pipeline, upload API endpoints, and database modules.

Run with:
    python -m pytest tests/test_phase2_ingestion.py -v
"""

import sys
import csv
import tempfile
import io
from pathlib import Path

import pytest
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ── Fixture: Flask test client ────────────────────────────
@pytest.fixture(scope="module")
def client():
    from backend.app import create_app
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── Fixture: minimal valid shipments CSV bytes ────────────
@pytest.fixture
def valid_shipments_csv() -> bytes:
    rows = [
        ["shipment_id", "origin_city", "destination_city",
         "scheduled_delivery", "is_delayed", "distance_km", "vehicle_type"],
        ["SHP-001", "Mumbai", "Delhi", "2023-06-01T10:00:00+00:00", "1", "1420", "Truck"],
        ["SHP-002", "Delhi", "Bangalore", "2023-06-02T14:00:00+00:00", "0", "2100", "Van"],
        ["SHP-003", "Mumbai", "Chennai", "2023-06-03T08:00:00+00:00", "1", "1340", "Air Cargo"],
    ]
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerows(rows)
    return buf.getvalue().encode()


@pytest.fixture
def valid_traffic_csv() -> bytes:
    rows = [
        ["route_id", "timestamp", "congestion_level", "avg_speed_kmh", "incident_flag"],
        ["MUM-DEL-NH48", "2023-06-01T08:00:00+00:00", "4", "32.5", "0"],
        ["DEL-BLR-NH44", "2023-06-01T09:00:00+00:00", "2", "65.0", "0"],
    ]
    buf = io.StringIO()
    csv.writer(buf).writerows(rows)
    return buf.getvalue().encode()


@pytest.fixture
def valid_weather_csv() -> bytes:
    rows = [
        ["city", "timestamp", "condition", "temperature_c", "wind_speed_kmh"],
        ["Mumbai", "2023-06-01T06:00:00+00:00", "Rain", "29.5", "35.0"],
        ["Delhi", "2023-06-01T06:00:00+00:00", "Clear", "38.0", "12.0"],
    ]
    buf = io.StringIO()
    csv.writer(buf).writerows(rows)
    return buf.getvalue().encode()


@pytest.fixture
def valid_gps_csv() -> bytes:
    rows = [
        ["shipment_id", "timestamp", "latitude", "longitude", "speed_kmh"],
        ["SHP-001", "2023-06-01T10:00:00+00:00", "19.076", "72.877", "0.0"],
        ["SHP-001", "2023-06-01T14:00:00+00:00", "23.123", "75.456", "72.0"],
    ]
    buf = io.StringIO()
    csv.writer(buf).writerows(rows)
    return buf.getvalue().encode()


# ════════════════════════════════════════════════════════════
# 1. Sample Data Generation Tests
# ════════════════════════════════════════════════════════════
class TestSampleDataGeneration:

    def test_sample_files_exist_or_can_be_generated(self):
        """Sample CSVs must exist in data/sample/ (run generator if missing)."""
        from backend.config import Config
        sample_dir = Config.SAMPLE_DIR
        expected = [
            "sample_shipments.csv", "sample_traffic.csv",
            "sample_weather.csv",   "sample_gps.csv",
        ]
        for fname in expected:
            path = sample_dir / fname
            assert path.exists(), (
                f"{fname} not found. Run: python scripts/generate_sample_data.py"
            )

    def test_sample_shipments_has_required_columns(self):
        from backend.config import Config
        df = pd.read_csv(Config.SAMPLE_DIR / "sample_shipments.csv", nrows=5)
        required = {"shipment_id", "origin_city", "destination_city",
                    "scheduled_delivery", "is_delayed"}
        assert required.issubset(set(df.columns)), \
            f"Missing: {required - set(df.columns)}"

    def test_sample_shipments_is_labelled_synthetic(self):
        from backend.config import Config
        df = pd.read_csv(Config.SAMPLE_DIR / "sample_shipments.csv", nrows=5)
        assert "data_source" in df.columns, "data_source column missing"
        assert "SYNTHETIC" in df["data_source"].iloc[0].upper()

    def test_sample_shipments_delay_rate_is_reasonable(self):
        """Delay rate should be between 20% and 70% (synthetic but realistic)."""
        from backend.config import Config
        df = pd.read_csv(Config.SAMPLE_DIR / "sample_shipments.csv")
        rate = df["is_delayed"].mean()
        assert 0.20 <= rate <= 0.70, f"Delay rate {rate:.1%} outside expected 20–70%"

    def test_no_duplicate_shipment_ids(self):
        from backend.config import Config
        df = pd.read_csv(Config.SAMPLE_DIR / "sample_shipments.csv")
        assert df["shipment_id"].is_unique, "Duplicate shipment_ids found"

    def test_gps_coordinates_in_valid_range(self):
        from backend.config import Config
        df = pd.read_csv(Config.SAMPLE_DIR / "sample_gps.csv")
        assert df["latitude"].between(-90, 90).all(), "Invalid GPS latitude"
        assert df["longitude"].between(-180, 180).all(), "Invalid GPS longitude"

    def test_weather_conditions_are_known_values(self):
        from backend.config import Config
        df = pd.read_csv(Config.SAMPLE_DIR / "sample_weather.csv")
        known = {"Clear", "Rain", "Fog", "Storm", "Snow", "Cloudy", "Drizzle"}
        actual = set(df["condition"].unique())
        unknown = actual - known
        assert not unknown, f"Unknown weather conditions: {unknown}"


# ════════════════════════════════════════════════════════════
# 2. Storage Service Tests
# ════════════════════════════════════════════════════════════
class TestStorageService:

    def test_storage_service_initialises(self):
        from backend.services.storage_service import StorageService
        svc = StorageService()
        assert svc.mode in ("local", "hdfs")

    def test_storage_mode_is_local_by_default(self):
        from backend.config import Config
        assert Config.STORAGE_MODE == "local"

    def test_save_and_retrieve_file(self, tmp_path):
        from backend.services.storage_service import StorageService
        svc = StorageService()

        # Write a temp CSV
        test_csv = tmp_path / "test_upload.csv"
        test_csv.write_text("shipment_id,origin_city\nSHP-001,Mumbai\n")

        dest = svc.save_file(test_csv, "shipments", "test_upload.csv")
        assert Path(dest).exists(), f"Saved file not found: {dest}"

    def test_list_files_returns_list(self):
        from backend.services.storage_service import StorageService
        svc = StorageService()
        files = svc.list_files("raw/shipments")
        assert isinstance(files, list)

    def test_get_storage_info_has_mode(self):
        from backend.services.storage_service import StorageService
        svc = StorageService()
        info = svc.get_storage_info()
        assert "mode" in info
        assert info["mode"] in ("local", "hdfs")


# ════════════════════════════════════════════════════════════
# 3. Ingestion Service Tests
# ════════════════════════════════════════════════════════════
class TestIngestionService:

    def _write_temp_csv(self, data: bytes, suffix=".csv") -> Path:
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=suffix, mode="wb"
        ) as f:
            f.write(data)
            return Path(f.name)

    def test_ingest_valid_shipments_csv(self, valid_shipments_csv):
        from backend.services.ingestion_service import IngestionService
        svc = IngestionService()
        path = self._write_temp_csv(valid_shipments_csv)
        try:
            report = svc.ingest_file(path, "shipments", "test.csv")
            assert report["records_read"] == 3
            # records_inserted may be 0 if MongoDB not running — that is OK
            assert report["records_read"] >= report["records_inserted"]
            assert isinstance(report["errors"], list)
        finally:
            path.unlink(missing_ok=True)

    def test_ingest_empty_csv_reports_error(self):
        from backend.services.ingestion_service import IngestionService
        svc = IngestionService()
        path = self._write_temp_csv(b"")  # empty file
        try:
            report = svc.ingest_file(path, "shipments", "empty.csv")
            assert report["success"] is False
            assert len(report["errors"]) > 0
        finally:
            path.unlink(missing_ok=True)

    def test_ingest_csv_with_missing_required_column(self):
        from backend.services.ingestion_service import IngestionService
        bad_csv = b"col_a,col_b\nval1,val2\n"
        svc = IngestionService()
        path = self._write_temp_csv(bad_csv)
        try:
            report = svc.ingest_file(path, "shipments", "bad.csv")
            assert report["success"] is False
            assert any("missing" in e.lower() for e in report["errors"])
        finally:
            path.unlink(missing_ok=True)

    def test_ingest_traffic_csv(self, valid_traffic_csv):
        from backend.services.ingestion_service import IngestionService
        svc = IngestionService()
        path = self._write_temp_csv(valid_traffic_csv)
        try:
            report = svc.ingest_file(path, "traffic", "traffic.csv")
            assert report["records_read"] == 2
        finally:
            path.unlink(missing_ok=True)

    def test_ingest_weather_csv(self, valid_weather_csv):
        from backend.services.ingestion_service import IngestionService
        svc = IngestionService()
        path = self._write_temp_csv(valid_weather_csv)
        try:
            report = svc.ingest_file(path, "weather", "weather.csv")
            assert report["records_read"] == 2
        finally:
            path.unlink(missing_ok=True)

    def test_ingest_gps_csv(self, valid_gps_csv):
        from backend.services.ingestion_service import IngestionService
        svc = IngestionService()
        path = self._write_temp_csv(valid_gps_csv)
        try:
            report = svc.ingest_file(path, "gps", "gps.csv")
            assert report["records_read"] == 2
        finally:
            path.unlink(missing_ok=True)

    def test_report_has_duration(self, valid_shipments_csv):
        from backend.services.ingestion_service import IngestionService
        svc = IngestionService()
        path = self._write_temp_csv(valid_shipments_csv)
        try:
            report = svc.ingest_file(path, "shipments", "test.csv")
            assert "duration_seconds" in report
            assert report["duration_seconds"] >= 0
        finally:
            path.unlink(missing_ok=True)


# ════════════════════════════════════════════════════════════
# 4. Upload API Endpoint Tests
# ════════════════════════════════════════════════════════════
class TestUploadEndpoints:

    def test_upload_valid_shipments(self, client, valid_shipments_csv):
        resp = client.post(
            "/api/v1/upload/shipments",
            data={"file": (io.BytesIO(valid_shipments_csv), "shipments.csv")},
            content_type="multipart/form-data",
        )
        assert resp.status_code in (201, 422)  # 422 only if columns fail
        data = resp.get_json()
        assert "success" in data

    def test_upload_invalid_type_returns_400(self, client, valid_shipments_csv):
        resp = client.post(
            "/api/v1/upload/unknown_type",
            data={"file": (io.BytesIO(valid_shipments_csv), "test.csv")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400
        assert resp.get_json()["success"] is False

    def test_upload_no_file_returns_400(self, client):
        resp = client.post("/api/v1/upload/shipments")
        assert resp.status_code == 400

    def test_upload_wrong_extension_returns_400(self, client):
        resp = client.post(
            "/api/v1/upload/shipments",
            data={"file": (io.BytesIO(b"data"), "file.xlsx")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400
        assert "csv" in resp.get_json()["message"].lower()

    def test_list_files_endpoint(self, client):
        resp = client.get("/api/v1/upload/files")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "files" in data["data"]
        assert isinstance(data["data"]["files"], list)

    def test_upload_traffic_csv(self, client, valid_traffic_csv):
        resp = client.post(
            "/api/v1/upload/traffic",
            data={"file": (io.BytesIO(valid_traffic_csv), "traffic.csv")},
            content_type="multipart/form-data",
        )
        assert resp.status_code in (201, 422)

    def test_upload_weather_csv(self, client, valid_weather_csv):
        resp = client.post(
            "/api/v1/upload/weather",
            data={"file": (io.BytesIO(valid_weather_csv), "weather.csv")},
            content_type="multipart/form-data",
        )
        assert resp.status_code in (201, 422)

