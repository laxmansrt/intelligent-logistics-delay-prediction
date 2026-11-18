"""
bigdata/spark/delay_aggregator.py
=================================
Multi-dimensional Delay Aggregator (PySpark + Local Fallback).
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Config
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def aggregate_delay_statistics(
    clean_csv_path: str | Path | None = None,
    output_json_path: str | Path | None = None,
) -> dict[str, Any]:
    start_time = datetime.now(timezone.utc)

    if clean_csv_path is None:
        clean_csv_path = Config.DATA_DIR / "processed" / "shipments_clean" / "clean_shipments.csv"
        if not Path(clean_csv_path).exists():
            clean_csv_path = Config.DATA_DIR / "sample" / "sample_shipments.csv"

    input_path = Path(clean_csv_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Shipment dataset not found: {input_path}")

    if output_json_path is None:
        output_json_path = Config.DATA_DIR / "analytics" / "delay_aggregations.json"
    output_path = Path(output_json_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        from bigdata.spark.spark_session import get_spark_session
        from pyspark.sql import functions as F

        spark = get_spark_session("DelayAggregator")
        df = spark.read.option("header", "true").option("inferSchema", "true").csv(str(input_path))

        total_count = df.count()
        delayed_count = df.filter(F.col("is_delayed") == 1).count()
        on_time_count = total_count - delayed_count
        delay_rate_pct = round((delayed_count / total_count * 100.0), 2) if total_count > 0 else 0.0
        avg_delay_min = (
            df.filter(F.col("is_delayed") == 1)
            .select(F.round(F.avg("delay_minutes"), 1))
            .first()[0] or 0.0
        )

        carrier_df = (
            df.groupBy("carrier")
            .agg(
                F.count("shipment_id").alias("total"),
                F.sum("is_delayed").alias("delayed"),
                F.round((F.sum("is_delayed") / F.count("shipment_id")) * 100.0, 1).alias("delay_rate"),
                F.round(F.coalesce(F.avg(F.when(F.col("is_delayed") == 1, F.col("delay_minutes"))), F.lit(0.0)), 1).alias("avg_delay"),
            )
            .sort(F.desc("delay_rate"))
        )
        by_carrier = carrier_df.toPandas().to_dict(orient="records")

        vehicle_df = (
            df.groupBy("vehicle_type")
            .agg(
                F.count("shipment_id").alias("total"),
                F.sum("is_delayed").alias("delayed"),
                F.round((F.sum("is_delayed") / F.count("shipment_id")) * 100.0, 1).alias("delay_rate"),
            )
            .sort(F.desc("delay_rate"))
        )
        by_vehicle = vehicle_df.toPandas().to_dict(orient="records")

        reason_df = (
            df.filter(F.col("is_delayed") == 1)
            .groupBy("delay_reason")
            .agg(F.count("shipment_id").alias("count"))
            .sort(F.desc("count"))
        )
        by_reason = reason_df.toPandas().to_dict(orient="records")
        engine_used = "PySpark"

    except Exception as exc:
        logger.warning("Using local delay aggregation engine: %s", exc)
        pdf = pd.read_csv(input_path)
        total_count = len(pdf)
        delayed_count = int((pdf["is_delayed"] == 1).sum())
        on_time_count = total_count - delayed_count
        delay_rate_pct = round((delayed_count / total_count * 100.0), 2) if total_count > 0 else 0.0
        avg_delay_min = round(float(pdf[pdf["is_delayed"] == 1]["delay_minutes"].mean()), 1) if delayed_count > 0 else 0.0

        c_grp = pdf.groupby("carrier").agg(total=("shipment_id", "count"), delayed=("is_delayed", "sum")).reset_index()
        c_grp["delay_rate"] = ((c_grp["delayed"] / c_grp["total"]) * 100.0).round(1)
        by_carrier = c_grp.to_dict(orient="records")

        v_grp = pdf.groupby("vehicle_type").agg(total=("shipment_id", "count"), delayed=("is_delayed", "sum")).reset_index()
        v_grp["delay_rate"] = ((v_grp["delayed"] / v_grp["total"]) * 100.0).round(1)
        by_vehicle = v_grp.to_dict(orient="records")

        r_counts = pdf[pdf["is_delayed"] == 1]["delay_reason"].value_counts().reset_index()
        r_counts.columns = ["delay_reason", "count"]
        by_reason = r_counts.to_dict(orient="records")
        engine_used = "Local Engine"

    results = {
        "success": True,
        "engine": engine_used,
        "kpis": {
            "total_shipments": total_count,
            "on_time_shipments": on_time_count,
            "delayed_shipments": delayed_count,
            "delay_percentage": delay_rate_pct,
            "avg_delay_minutes": avg_delay_min,
        },
        "by_carrier": by_carrier,
        "by_vehicle": by_vehicle,
        "by_reason": by_reason,
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": round((datetime.now(timezone.utc) - start_time).total_seconds(), 2),
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    res = aggregate_delay_statistics()
    print("KPIs:", res["kpis"])
