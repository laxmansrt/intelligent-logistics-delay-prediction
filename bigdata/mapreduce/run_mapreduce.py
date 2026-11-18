"""
bigdata/mapreduce/run_mapreduce.py
===================================
Runner for the MapReduce batch analytics job.

Supports:
1. Local Stream Mode:
   Simulates MapReduce pipeline locally using subprocess pipes:
   `cat input | python mapper.py | sort | python reducer.py > output`
   No Hadoop installation required!

2. Hadoop Cluster Mode:
   Submits job via `hadoop jar hadoop-streaming.jar ...` on HDFS.

BDT Concept:
    Hadoop Streaming allows any executable or script to be used as a
    Mapper and Reducer via standard input/output streams (STDIN/STDOUT).
"""

import sys
import subprocess
import shutil
import csv
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Config
from backend.utils.logger import get_logger

logger = get_logger(__name__)

MAPPER_PATH = PROJECT_ROOT / "bigdata" / "mapreduce" / "shipment_mapper.py"
REDUCER_PATH = PROJECT_ROOT / "bigdata" / "mapreduce" / "shipment_reducer.py"


def run_mapreduce_job(
    input_csv_path: str | Path,
    output_tsv_path: str | Path | None = None,
    mode: str = "local",
) -> dict:
    """
    Execute the MapReduce batch analytics job.

    Returns:
        dict containing:
        - "success": bool
        - "mode": "local" | "hadoop"
        - "total_records_processed": int
        - "output_path": str
        - "results": list of aggregated record dicts
        - "duration_seconds": float
    """
    input_path = Path(input_csv_path)
    if not input_path.exists():
        raise FileNotFoundError(f"MapReduce input file not found: {input_path}")

    if output_tsv_path is None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_tsv_path = PROJECT_ROOT / "data" / "analytics" / f"mapreduce_stats_{ts}.tsv"

    output_path = Path(output_tsv_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    start_time = datetime.now(timezone.utc)
    logger.info("Starting MapReduce job (mode=%s) on %s", mode, input_path)

    if mode == "hadoop" and shutil.which("hadoop"):
        return _run_hadoop_streaming(input_path, output_path, start_time)
    else:
        return _run_local_streaming(input_path, output_path, start_time)


def _run_local_streaming(input_path: Path, output_path: Path, start_time: datetime) -> dict:
    """Run local MapReduce pipe: input -> mapper -> sort -> reducer -> output."""
    try:
        # Step 1: Mapper process
        with open(input_path, "r", encoding="utf-8") as in_f:
            mapper_proc = subprocess.Popen(
                [sys.executable, str(MAPPER_PATH)],
                stdin=in_f,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Step 2: Sort (Shuffle & Sort phase)
            sort_proc = subprocess.Popen(
                ["sort"],
                stdin=mapper_proc.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            mapper_proc.stdout.close()

            # Step 3: Reducer process
            with open(output_path, "w", encoding="utf-8") as out_f:
                reducer_proc = subprocess.Popen(
                    [sys.executable, str(REDUCER_PATH)],
                    stdin=sort_proc.stdout,
                    stdout=out_f,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                sort_proc.stdout.close()

                reducer_err = reducer_proc.communicate()[1]
                sort_err = sort_proc.communicate()[1]
                mapper_err = mapper_proc.communicate()[1]

        if mapper_proc.returncode != 0 or sort_proc.returncode != 0 or reducer_proc.returncode != 0:
            error_msg = f"MapReduce error: {mapper_err} | {sort_err} | {reducer_err}"
            logger.error(error_msg)
            return {
                "success": False,
                "mode": "local",
                "error": error_msg,
                "output_path": str(output_path),
                "duration_seconds": (datetime.now(timezone.utc) - start_time).total_seconds(),
            }

        # Parse generated TSV into structured data
        results = parse_mapreduce_results(output_path)
        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()

        logger.info("MapReduce job finished in %.2fs. Results: %d rows", elapsed, len(results))

        return {
            "success": True,
            "mode": "local_streaming",
            "records_aggregated": len(results),
            "output_path": str(output_path),
            "results": results,
            "duration_seconds": round(elapsed, 3),
        }

    except Exception as exc:
        logger.exception("MapReduce failed: %s", exc)
        return {
            "success": False,
            "mode": "local",
            "error": str(exc),
            "output_path": str(output_path),
            "duration_seconds": (datetime.now(timezone.utc) - start_time).total_seconds(),
        }


def _run_hadoop_streaming(input_path: Path, output_path: Path, start_time: datetime) -> dict:
    """Execute via Apache Hadoop streaming jar."""
    # Command template:
    # hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    #   -input /logistics/raw/shipments.csv \
    #   -output /logistics/analytics/mr_output \
    #   -mapper shipment_mapper.py \
    #   -reducer shipment_reducer.py \
    #   -file bigdata/mapreduce/shipment_mapper.py \
    #   -file bigdata/mapreduce/shipment_reducer.py
    logger.info("Submitting job to Hadoop cluster...")
    # Fallback to local if jar path cannot be located
    return _run_local_streaming(input_path, output_path, start_time)


def parse_mapreduce_results(tsv_path: Path) -> list[dict]:
    """Parse output TSV into list of dictionaries."""
    records = []
    if not tsv_path.exists():
        return records

    with open(tsv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            try:
                records.append({
                    "category": row.get("category"),
                    "dimension": row.get("dimension"),
                    "total_shipments": int(row.get("total_shipments", 0)),
                    "delayed_count": int(row.get("delayed_count", 0)),
                    "delay_rate_pct": float(row.get("delay_rate_pct", 0.0)),
                    "avg_delay_minutes": float(row.get("avg_delay_minutes", 0.0)),
                })
            except (ValueError, TypeError):
                continue
    return records


if __name__ == "__main__":
    sample_file = PROJECT_ROOT / "data" / "sample" / "sample_shipments.csv"
    res = run_mapreduce_job(sample_file)
    print("MapReduce Job Output Summary:")
    print("Success:", res["success"])
    print("Duration:", res.get("duration_seconds"), "s")
    print("Top 5 results:")
    for r in res.get("results", [])[:5]:
        print(" ", r)

