#!/usr/bin/env python3
"""
bigdata/mapreduce/shipment_mapper.py
====================================
Hadoop Streaming Mapper for Logistics Batch Analytics.

BDT Concept:
    MapReduce is a distributed programming model invented for processing
    vast datasets on commodity clusters.
    The Mapper parses each incoming record independently (embarrassingly parallel)
    and maps it to intermediate key-value pairs:
        (Key, Value) -> (MetricCategory:DimensionKey, "total=1,delayed=X,delay_mins=Y")

Input (STDIN):
    CSV lines from shipments dataset.
    Header line is automatically detected and skipped.

Output (STDOUT):
    Tab-separated key-value pairs:
        <category>|<dimension>\t1\t<is_delayed>\t<delay_minutes>

Example outputs:
    route|Mumbai->Delhi\t1\t1\t145.0
    carrier|BlueDart\t1\t0\t0.0
    vehicle|Truck\t1\t1\t65.0
"""

import sys
import csv

def main():
    # Use csv.reader to safely handle quoted fields and commas
    reader = csv.reader(sys.stdin)
    header_found = False
    col_idx = {}

    for row in reader:
        if not row:
            continue

        # Detect and parse header
        if not header_found:
            row_lower = [c.strip().lower() for c in row]
            if "shipment_id" in row_lower and "is_delayed" in row_lower:
                col_idx = {col: i for i, col in enumerate(row_lower)}
                header_found = True
                continue
            else:
                # If no header detected on line 1, default canonical layout fallback
                col_idx = {
                    "origin_city": 1, "destination_city": 5, "vehicle_type": 10,
                    "carrier": 11, "is_delayed": 18, "delay_minutes": 19
                }
                header_found = True

        try:
            origin = row[col_idx["origin_city"]].strip() if "origin_city" in col_idx else "Unknown"
            destination = row[col_idx["destination_city"]].strip() if "destination_city" in col_idx else "Unknown"
            carrier = row[col_idx["carrier"]].strip() if "carrier" in col_idx else "Unknown"
            vehicle = row[col_idx["vehicle_type"]].strip() if "vehicle_type" in col_idx else "Unknown"

            delayed_val = row[col_idx["is_delayed"]].strip() if "is_delayed" in col_idx else "0"
            is_delayed = 1 if delayed_val in ("1", "true", "True", "yes", "Yes") else 0

            delay_mins_str = row[col_idx.get("delay_minutes", -1)].strip() if "delay_minutes" in col_idx else "0"
            try:
                delay_minutes = float(delay_mins_str) if delay_mins_str else 0.0
            except ValueError:
                delay_minutes = 0.0

            route = f"{origin}->{destination}"

            # Emit intermediate keys for Route, Carrier, and Vehicle Type
            print(f"route|{route}\t1\t{is_delayed}\t{delay_minutes:.1f}")
            print(f"carrier|{carrier}\t1\t{is_delayed}\t{delay_minutes:.1f}")
            print(f"vehicle|{vehicle}\t1\t{is_delayed}\t{delay_minutes:.1f}")
            print(f"overall|ALL\t1\t{is_delayed}\t{delay_minutes:.1f}")

        except (IndexError, ValueError):
            continue

if __name__ == "__main__":
    main()

