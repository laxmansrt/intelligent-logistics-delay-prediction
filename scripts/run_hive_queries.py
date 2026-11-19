"""
scripts/run_hive_queries.py
===========================
CLI script to execute Apache Hive DDL, data loading, and all 7 HiveQL analytical queries.

Usage:
    python scripts/run_hive_queries.py --init             # Initialize Hive database & load ORC tables
    python scripts/run_hive_queries.py --query all        # Run all 7 analytical HiveQL queries
    python scripts/run_hive_queries.py --query ontime_vs_delayed
"""

import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.hive_service import hive_service


def main():
    parser = argparse.ArgumentParser(description="Apache Hive Big Data Analytics Runner")
    parser.add_argument("--init", action="store_true", help="Initialize Hive database, tables, and load dataset")
    parser.add_argument(
        "--query",
        choices=[
            "total_shipments",
            "ontime_vs_delayed",
            "delay_percentage",
            "avg_delivery_duration",
            "routes_highest_delays",
            "transportation_mode_analysis",
            "monthly_shipment_trends",
            "all",
        ],
        default="all",
        help="Specific HiveQL query to execute",
    )
    args = parser.parse_args()

    print("=" * 75)
    print("  BIG DATA CLASSIFICATION AND PREDICTION USING APACHE HIVE")
    print("  Apache Hive Query & Storage Engine")
    print("=" * 75)

    if args.init:
        print("\n[Step 1/2] Initializing Hive Metastore & ORC Partitioned Tables...")
        res = hive_service.initialize_hive_schema()
        print(f"  ✓ Database : {res['database']}")
        print(f"  ✓ Table    : {res['table']} ({res['format']})")
        print(f"  ✓ Records  : {res['records_loaded']:,} rows loaded into warehouse")
        print(f"  ✓ Duration : {res['duration_seconds']}s")

    queries_to_run = [
        ("1. Total Number of Shipments", "total_shipments"),
        ("2. On-Time vs. Delayed Shipments Classification", "ontime_vs_delayed"),
        ("3. System Delay Percentage & Average Duration", "delay_percentage"),
        ("4. Average Delivery Duration by Transport Mode", "avg_delivery_duration"),
        ("5. Routes with Highest Delay Counts (Bottlenecks)", "routes_highest_delays"),
        ("6. Shipment Analysis by Transportation Mode", "transportation_mode_analysis"),
        ("7. Monthly Shipment Volume & Delay Trends", "monthly_shipment_trends"),
    ] if args.query == "all" else [(args.query, args.query)]

    print("\n--- Executing HiveQL Analytics ---")
    for title, q_id in queries_to_run:
        print(f"\n▶ {title}")
        res = hive_service.run_named_query(q_id)
        if res.get("success"):
            cols = res.get("columns", [])
            rows = res.get("rows", [])
            print("  Columns:", " | ".join(cols))
            for row in rows[:5]:
                print(" ", " | ".join(str(v) for v in row))
            if len(rows) > 5:
                print(f"  ... ({len(rows) - 5} more rows)")
            print(f"  Execution Time: {res.get('duration_seconds')}s")
        else:
            print("  ✗ Query Error:", res.get("error"))

    print("\n✅ Hive execution sequence complete.")


if __name__ == "__main__":
    main()
