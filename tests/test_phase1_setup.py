"""
tests/test_phase1_setup.py
===========================
Phase 1 tests: Verify the project structure, configuration, and Flask
skeleton are working correctly.

Run with:
    python -m pytest tests/test_phase1_setup.py -v
"""

import sys
import os
from pathlib import Path
import pytest

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ── Fixture: Flask test client ────────────────────────────
@pytest.fixture
def client():
    """Create a Flask test client for API testing."""
    from backend.app import create_app
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── 1. Project structure tests ────────────────────────────
class TestProjectStructure:
    """Verify all required directories and files exist."""

    REQUIRED_DIRS = [
        "backend", "backend/routes", "backend/services", "backend/utils",
        "bigdata/spark", "bigdata/mapreduce",
        "ml", "database",
        "data/raw/shipments", "data/raw/traffic", "data/raw/weather", "data/raw/gps",
        "data/processed", "data/analytics", "data/models", "data/sample",
        "frontend/templates", "frontend/static/css", "frontend/static/js",
        "scripts", "tests", "docs",
    ]

    REQUIRED_FILES = [
        "run.py",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "backend/__init__.py",
        "backend/app.py",
        "backend/config.py",
        "backend/extensions.py",
        "backend/routes/__init__.py",
        "backend/routes/health.py",
        "backend/utils/__init__.py",
        "backend/utils/logger.py",
        "backend/utils/response.py",
        "backend/utils/validators.py",
        "frontend/templates/index.html",
    ]

    def test_required_directories_exist(self):
        for d in self.REQUIRED_DIRS:
            path = PROJECT_ROOT / d
            assert path.is_dir(), f"Missing directory: {d}"

    def test_required_files_exist(self):
        for f in self.REQUIRED_FILES:
            path = PROJECT_ROOT / f
            assert path.is_file(), f"Missing file: {f}"

    def test_env_example_has_required_keys(self):
        env_example = (PROJECT_ROOT / ".env.example").read_text()
        required_keys = [
            "FLASK_SECRET_KEY", "STORAGE_MODE", "SPARK_MODE",
            "MONGO_URI", "MONGO_DB_NAME", "MAX_UPLOAD_MB",
        ]
        for key in required_keys:
            assert key in env_example, f"Missing key in .env.example: {key}"

    def test_env_example_does_not_contain_real_secrets(self):
        """Verify .env.example uses placeholder values, not real secrets."""
        env_example = (PROJECT_ROOT / ".env.example").read_text()
        # Should not contain what looks like a real secret
        assert "AKIA" not in env_example, "AWS key in .env.example"
        assert "sk-" not in env_example, "OpenAI key in .env.example"


# ── 2. Configuration tests ────────────────────────────────
class TestConfig:
    def test_config_loads_without_error(self):
        from backend.config import Config
        assert Config.STORAGE_MODE in ("local", "hdfs")
        assert Config.SPARK_MODE in ("local", "cluster")
        assert Config.MAX_UPLOAD_MB > 0

    def test_config_summary_is_safe(self):
        """Config summary must not expose secret key."""
        from backend.config import Config
        summary = Config.summary()
        assert "SECRET_KEY" not in str(summary)
        assert "secret" not in str(summary).lower()

    def test_allowed_extensions(self):
        from backend.config import Config
        assert "csv" in Config.ALLOWED_EXTENSIONS


# ── 3. Validator tests ────────────────────────────────────
class TestValidators:
    def test_allowed_file_csv(self):
        from backend.utils.validators import allowed_file
        assert allowed_file("shipments.csv") is True

    def test_allowed_file_reject_exe(self):
        from backend.utils.validators import allowed_file
        assert allowed_file("malware.exe") is False

    def test_allowed_file_reject_no_extension(self):
        from backend.utils.validators import allowed_file
        assert allowed_file("noextension") is False

    def test_validate_csv_columns_ok(self):
        from backend.utils.validators import validate_csv_columns
        cols = ["shipment_id", "origin_city", "destination_city",
                "scheduled_delivery", "is_delayed", "extra_col"]
        ok, msg = validate_csv_columns(cols, "shipments")
        assert ok is True, msg

    def test_validate_csv_columns_missing(self):
        from backend.utils.validators import validate_csv_columns
        cols = ["shipment_id", "origin_city"]  # missing required cols
        ok, msg = validate_csv_columns(cols, "shipments")
        assert ok is False
        assert "missing" in msg.lower()

    def test_validate_csv_columns_unknown_type(self):
        from backend.utils.validators import validate_csv_columns
        ok, msg = validate_csv_columns(["a", "b"], "unknown_dataset")
        assert ok is False

    def test_sanitise_filename(self):
        from backend.utils.validators import sanitise_filename
        assert sanitise_filename("my file (1).csv") == "my_file_1.csv"
        assert sanitise_filename("../../etc/passwd") == "passwd"


# ── 4. Flask API tests ────────────────────────────────────
class TestHealthEndpoints:
    def test_liveness_returns_200(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200

    def test_liveness_response_shape(self, client):
        resp = client.get("/api/v1/health")
        data = resp.get_json()
        assert data["success"] is True
        assert "data" in data
        assert "timestamp" in data

    def test_detail_returns_200(self, client):
        resp = client.get("/api/v1/health/detail")
        assert resp.status_code == 200

    def test_detail_has_components(self, client):
        resp = client.get("/api/v1/health/detail")
        data = resp.get_json()
        assert "components" in data["data"]
        assert "storage" in data["data"]["components"]
        assert "spark" in data["data"]["components"]

    def test_404_returns_json(self, client):
        resp = client.get("/api/v1/nonexistent_route")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["success"] is False

    def test_index_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"Logistics" in resp.data or b"BDT" in resp.data


# ── 5. Logger tests ───────────────────────────────────────
class TestLogger:
    def test_get_logger_returns_logger(self):
        from backend.utils.logger import get_logger
        logger = get_logger("test.module")
        assert logger is not None
        assert logger.name == "test.module"

    def test_logger_does_not_duplicate_handlers(self):
        from backend.utils.logger import get_logger
        logger1 = get_logger("test.dedup")
        logger2 = get_logger("test.dedup")
        assert logger1 is logger2
        assert len(logger1.handlers) > 0

