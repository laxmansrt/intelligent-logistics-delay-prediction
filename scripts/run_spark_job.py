"""
scripts/run_spark_job.py
========================
CLI script to trigger PySpark jobs from the command line.

Usage:
    python scripts/run_spark_job.py --job etl
    python scripts/run_spark_job.py --job routes
    python scripts/run_spark_job.py --job delays
    python scripts/run_spark_job.py --job all
"""

import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Config
from backend.services.spark_service import spark_service


def main():
    parser = argparse.ArgumentParser(description="Run PySpark Logistics Analytics Jobs")
    parser.add_argument(
        "--job",
        choices=["etl", "routes", "delays", "all"],
        default="all",
        help="Specific PySpark job to execute (default: all)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  LOGISTICS BIG DATA PROCESSING (PySpark)")
    print(f"  Spark Master: {Config.SPARK_MASTER}")
    print(f"  Storage Mode: {Config.STORAGE_MODE}")
    print("=" * 60)

    if args.job in ("etl", "all"):
        print("\n[1/3] Executing Shipment ETL Pipeline...")
        res = spark_service.run_etl_job()
        print("  Status:", "Success" if res.get("success") else "Failed")
        if res.get("success"):
            print(f"  Processed {res.get('final_records')} clean records ({res.get('duplicates_removed')} duplicates removed)")

    if args.job in ("routes", "all"):
        print("\n[2/3] Analyzing Route Delays and Bottlenecks...")
        res = spark_service.run_route_analysis()
        print("  Status:", "Success" if res.get("success") else "Failed")
        if res.get("success"):
            print(f"  Analyzed {res.get('total_routes_analyzed')} routes")

    if args.job in ("delays", "all"):
        print("\n[3/3] Aggregating Multi-dimensional Delay Metrics...")
        res = spark_service.run_delay_aggregation()
        print("  Status:", "Success" if res.get("success") else "Failed")
        if res.get("success"):
            kpis = res.get("kpis", {})
            print(f"  KPIs: {kpis.get('total_shipments')} shipments | Delay Rate: {kpis.get('delay_percentage')}%")

    print("\n✅ Spark processing sequence complete.")


if __name__ == "__main__":
    main()

