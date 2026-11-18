"""
backend/config.py
=================
Loads all configuration from environment variables (.env file).
Uses python-dotenv so values in .env are automatically picked up.

BDT Concept: Externalising configuration is a 12-factor app best practice.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from project root (parent of backend/)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """
    Central configuration class.
    All settings are read from environment variables with safe defaults.
    """

    # ── Flask ──────────────────────────────────────────────
    SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-prod")
    DEBUG: bool = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")

    # ── MongoDB ────────────────────────────────────────────
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "logistics_bdt")

    # ── Storage Mode ───────────────────────────────────────
    # "local"  → data/ directory on this machine
    # "hdfs"   → Apache HDFS cluster
    STORAGE_MODE: str = os.getenv("STORAGE_MODE", "local").lower()

    # ── Spark ──────────────────────────────────────────────
    SPARK_MODE: str = os.getenv("SPARK_MODE", "local").lower()
    SPARK_MASTER: str = os.getenv("SPARK_MASTER", "local[*]")

    # ── HDFS (only used when STORAGE_MODE=hdfs) ────────────
    HDFS_HOST: str = os.getenv("HDFS_HOST", "localhost")
    HDFS_PORT: int = int(os.getenv("HDFS_PORT", "9000"))
    HDFS_USER: str = os.getenv("HDFS_USER", "hdfs")
    HDFS_BASE_PATH: str = os.getenv("HDFS_BASE_PATH", "/logistics")

    # ── File Uploads ───────────────────────────────────────
    MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "50"))
    MAX_CONTENT_LENGTH: int = MAX_UPLOAD_MB * 1024 * 1024  # bytes for Flask
    ALLOWED_EXTENSIONS: set = set(
        os.getenv("ALLOWED_EXTENSIONS", "csv").split(",")
    )

    # ── Filesystem Paths ───────────────────────────────────
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    ANALYTICS_DIR: Path = DATA_DIR / "analytics"
    MODELS_DIR: Path = DATA_DIR / "models"
    SAMPLE_DIR: Path = DATA_DIR / "sample"
    UPLOAD_FOLDER: Path = RAW_DIR  # Flask uses this for uploads

    # ── Machine Learning ───────────────────────────────────
    MODEL_DIR: Path = BASE_DIR / os.getenv("MODEL_DIR", "data/models")
    MODEL_VERSION: str = os.getenv("MODEL_VERSION", "rf_v1.0")
    RANDOM_STATE: int = int(os.getenv("RANDOM_STATE", "42"))

    # ── Logging ────────────────────────────────────────────
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_DIR: Path = BASE_DIR / os.getenv("LOG_DIR", "logs")

    @classmethod
    def ensure_directories(cls) -> None:
        """Create required local directories if they don't exist."""
        dirs = [
            cls.RAW_DIR / "shipments",
            cls.RAW_DIR / "traffic",
            cls.RAW_DIR / "weather",
            cls.RAW_DIR / "gps",
            cls.PROCESSED_DIR,
            cls.ANALYTICS_DIR,
            cls.MODELS_DIR,
            cls.SAMPLE_DIR,
            cls.LOG_DIR,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

    @classmethod
    def summary(cls) -> dict:
        """Return a safe (non-secret) config summary for the health endpoint."""
        return {
            "storage_mode": cls.STORAGE_MODE,
            "spark_mode": cls.SPARK_MODE,
            "spark_master": cls.SPARK_MASTER,
            "mongo_db": cls.MONGO_DB_NAME,
            "max_upload_mb": cls.MAX_UPLOAD_MB,
            "model_version": cls.MODEL_VERSION,
        }

