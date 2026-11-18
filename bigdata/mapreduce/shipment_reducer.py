#!/usr/bin/env python3
"""
bigdata/mapreduce/shipment_reducer.py
=====================================
Hadoop Streaming Reducer for Logistics Batch Analytics.

BDT Concept:
    The Reducer receives intermediate keys and values grouped and sorted
    by the MapReduce framework's Shuffle & Sort phase.
    It performs an aggregation over all values for each key:
        Sum(total_shipments), Sum(delayed_shipments), Avg(delay_minutes)

Input (STDIN):
    Sorted lines from Shuffle & Sort:
    <category>|<dimension>\t1\t<is_delayed>\t<delay_minutes>

Output (STDOUT):
    <category>\t<dimension>\t<total_shipments>\t<delayed_count>\t<delay_rate_pct>\t<avg_delay_mins>
"""

import sys

def main():
    current_key = None
    total_count = 0
    delayed_count = 0
    total_delay_minutes = 0.0

    print("category\tdimension\ttotal_shipments\tdelayed_count\tdelay_rate_pct\tavg_delay_minutes")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) < 4:
            continue

        key, count_str, delayed_str, delay_mins_str = parts[0], parts[1], parts[2], parts[3]

        try:
            count = int(count_str)
            delayed = int(delayed_str)
            delay_mins = float(delay_mins_str)
        except ValueError:
            continue

        if current_key and current_key != key:
            # Emit aggregated metrics for the previous key
            emit_metrics(current_key, total_count, delayed_count, total_delay_minutes)
            total_count = 0
            delayed_count = 0
            total_delay_minutes = 0.0

        current_key = key
        total_count += count
        delayed_count += delayed
        total_delay_minutes += delay_mins

    # Emit final key
    if current_key and total_count > 0:
        emit_metrics(current_key, total_count, delayed_count, total_delay_minutes)


def emit_metrics(key: str, total: int, delayed: int, total_delay_mins: float):
    if total <= 0:
        return
    delay_rate = (delayed / total) * 100.0
    avg_delay = (total_delay_mins / delayed) if delayed > 0 else 0.0

    if "|" in key:
        category, dimension = key.split("|", 1)
    else:
        category, dimension = "unknown", key

    print(f"{category}\t{dimension}\t{total}\t{delayed}\t{delay_rate:.2f}\t{avg_delay:.2f}")


if __name__ == "__main__":
    main()

