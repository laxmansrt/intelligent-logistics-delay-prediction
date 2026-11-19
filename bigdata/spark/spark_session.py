"""
bigdata/spark/spark_session.py
==============================
SparkSession Factory for Distributed Big Data Processing.

BDT Concept:
    The SparkSession is the unified entry point for reading data,
    registering DataFrames as tables, and executing distributed SQL/DataFrame
    transformations via Spark's Catalyst Optimizer and Tungsten execution engine.

    Modes supported:
    - SPARK_MODE=local: Runs in-process with local[*] threads matching host CPU cores.
    - SPARK_MODE=cluster: Connects to a standalone Spark Master or YARN resource manager.
"""

import os
import sys
from pathlib import Path
from backend.config import Config
from backend.utils.logger import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_spark_session = None

def get_spark_session(app_name: str = "LogisticsDelayAnalytics"):
    """
    Create or retrieve an active SparkSession instance.

    Configures:
    - Master URL (local[*] or cluster)
    - Memory allocation
    - Serializer (Kryo for high performance)
    - SQL warehouse directory in data/processed/spark-warehouse
    """
    global _spark_session

    if _spark_session is not None:
        try:
            # Check if active
            _spark_session.sparkContext.getConf()
            return _spark_session
        except Exception:
            _spark_session = None

    try:
        from pyspark.sql import SparkSession
    except ImportError as e:
        logger.error("PySpark is not installed: %s. Install with: pip install pyspark", e)
        raise RuntimeError("PySpark is not installed.") from e

    warehouse_dir = str(PROJECT_ROOT / "bigdata" / "hive" / "warehouse")
    os.makedirs(warehouse_dir, exist_ok=True)

    master = Config.SPARK_MASTER if Config.SPARK_MODE == "local" else Config.SPARK_MASTER
    logger.info("Initializing SparkSession '%s' (master: %s)", app_name, master)

    builder = (
        SparkSession.builder
        .appName(app_name)
        .master(master)
        .config("spark.sql.warehouse.dir", warehouse_dir)
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "4")  # Optimized for local dev
        .config("spark.ui.enabled", "false")          # Disable web UI in local test mode
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .config("spark.sql.catalogImplementation", "hive")
        .config("hive.metastore.warehouse.dir", warehouse_dir)
        .enableHiveSupport()
    )

    try:
        spark = builder.getOrCreate()
        # Suppress verbose INFO logs in stdout
        spark.sparkContext.setLogLevel("WARN")
        _spark_session = spark
        logger.info("SparkSession initialized successfully. Spark version: %s", spark.version)
        return spark
    except Exception as exc:
        logger.exception("Failed to start SparkSession: %s", exc)
        raise


def stop_spark_session():
    """Safely terminate the active SparkSession."""
    global _spark_session
    if _spark_session is not None:
        try:
            _spark_session.stop()
            logger.info("SparkSession stopped.")
        except Exception as e:
            logger.warning("Error stopping SparkSession: %s", e)
        finally:
            _spark_session = None

