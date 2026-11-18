"""
bigdata/spark/shipment_processor.py
===================================
PySpark ETL Pipeline for Shipment, Weather, and Traffic Data.

BDT Concept:
    Apache Spark processes big data in-memory using Resilient Distributed
    Datasets (RDDs) and high-level DataFrames.
    This module performs:
    1. Schema enforcement and type casting.
    2. Distributed deduplication (.dropDuplicates).
    3. Missing value imputation.
    4. Feature derivation (date-time components, route keys).
    5. Clean dataset persistence to data/processed/.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Config
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def process_shipments(
    input_csv_path: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """
    Run ETL pipeline on shipment data using PySpark (with local DataFrame fallback).
    """
    start_time = datetime.now(timezone.utc)

    if input_csv_path is None:
        input_csv_path = Config.DATA_DIR / "sample" / "sample_shipments.csv"
    input_path = Path(input_csv_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_dir is None:
        output_dir = Config.DATA_DIR / "processed" / "shipments_clean"
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    final_csv_file = output_path / "clean_shipments.csv"

    # Try PySpark execution
    try:
        from bigdata.spark.spark_session import get_spark_session
        from pyspark.sql import functions as F
        from pyspark.sql.types import DoubleType, IntegerType

        spark = get_spark_session("ShipmentETLProcessor")
        logger.info("Reading raw shipments with PySpark from %s", input_path)
        raw_df = spark.read.option("header", "true").option("inferSchema", "true").csv(str(input_path))
        initial_count = raw_df.count()

        dedup_df = raw_df.dropDuplicates(["shipment_id"])
        dedup_count = dedup_df.count()
        duplicates_removed = initial_count - dedup_count

        clean_df = (
            dedup_df
            .withColumn("distance_km", F.col("distance_km").cast(DoubleType()))
            .withColumn("weight_kg", F.col("weight_kg").cast(DoubleType()))
            .withColumn("is_delayed", F.coalesce(F.col("is_delayed").cast(IntegerType()), F.lit(0)))
            .withColumn("delay_minutes", F.coalesce(F.col("delay_minutes").cast(DoubleType()), F.lit(0.0)))
            .withColumn("scheduled_pickup_ts", F.to_timestamp(F.col("scheduled_pickup")))
            .withColumn("scheduled_delivery_ts", F.to_timestamp(F.col("scheduled_delivery")))
        )

        avg_distance = clean_df.select(F.avg("distance_km")).first()[0] or 500.0
        avg_weight = clean_df.select(F.avg("weight_kg")).first()[0] or 150.0

        clean_df = clean_df.na.fill({
            "distance_km": avg_distance,
            "weight_kg": avg_weight,
            "vehicle_type": "Truck",
            "carrier": "Standard",
            "origin_city": "Unknown",
            "destination_city": "Unknown",
            "delay_reason": "No Delay",
        })

        processed_df = (
            clean_df
            .withColumn("route", F.concat(F.col("origin_city"), F.lit("->"), F.col("destination_city")))
            .withColumn("scheduled_hour", F.hour(F.col("scheduled_pickup_ts")))
            .withColumn("scheduled_day_of_week", F.dayofweek(F.col("scheduled_pickup_ts")))
            .withColumn("scheduled_month", F.month(F.col("scheduled_pickup_ts")))
            .withColumn(
                "planned_transit_hours",
                F.round((F.unix_timestamp("scheduled_delivery_ts") - F.unix_timestamp("scheduled_pickup_ts")) / 3600.0, 2)
            )
        )

        final_count = processed_df.count()
        pandas_df = processed_df.toPandas()
        pandas_df.to_csv(final_csv_file, index=False)
        engine_used = "PySpark"

    except Exception as spark_err:
        logger.warning("PySpark unavailable or failed: %s. Using local execution engine.", spark_err)
        # Local DataFrame Engine Fallback
        df = pd.read_csv(input_path)
        initial_count = len(df)
        df = df.drop_duplicates(subset=["shipment_id"])
        duplicates_removed = initial_count - len(df)

        df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce").fillna(500.0)
        df["weight_kg"] = pd.to_numeric(df["weight_kg"], errors="coerce").fillna(150.0)
        df["is_delayed"] = pd.to_numeric(df["is_delayed"], errors="coerce").fillna(0).astype(int)
        df["delay_minutes"] = pd.to_numeric(df["delay_minutes"], errors="coerce").fillna(0.0)

        dt_pickup = pd.to_datetime(df["scheduled_pickup"], errors="coerce")
        dt_delivery = pd.to_datetime(df["scheduled_delivery"], errors="coerce")
        df["route"] = df["origin_city"] + "->" + df["destination_city"]
        df["scheduled_hour"] = dt_pickup.dt.hour.fillna(10).astype(int)
        df["scheduled_day_of_week"] = getattr(dt_pickup.dt, "day_of_week", dt_pickup.dt.dayofweek).fillna(2).astype(int)
        df["scheduled_month"] = dt_pickup.dt.month.fillna(6).astype(int)
        df["planned_transit_hours"] = ((dt_delivery - dt_pickup).dt.total_seconds() / 3600.0).round(2).fillna(24.0)

        df.to_csv(final_csv_file, index=False)
        final_count = len(df)
        engine_used = "Local BigData Engine (Pandas Fallback)"

    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
    logger.info("ETL complete in %.2fs: %d rows processed via %s", elapsed, final_count, engine_used)

    return {
        "success": True,
        "engine": engine_used,
        "job_name": "Shipment_ETL",
        "raw_records": initial_count,
        "duplicates_removed": duplicates_removed,
        "final_records": final_count,
        "output_path": str(final_csv_file),
        "duration_seconds": round(elapsed, 2),
    }


if __name__ == "__main__":
    res = process_shipments()
    print("ETL Result:", res)
