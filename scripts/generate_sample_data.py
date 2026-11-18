"""
scripts/generate_sample_data.py
================================
Generates SYNTHETIC sample datasets for demonstration purposes.

⚠️  IMPORTANT — DATA DISCLOSURE:
    All data produced by this script is SYNTHETICALLY GENERATED.
    It does NOT represent real shipments, real routes, or real events.
    It is provided ONLY so students can run the system without a real dataset.
    Replace with a real dataset (e.g. from Kaggle) for genuine analytics.

Datasets generated:
    data/sample/sample_shipments.csv   (~2000 rows)
    data/sample/sample_traffic.csv     (~3000 rows)
    data/sample/sample_weather.csv     (~1500 rows)
    data/sample/sample_gps.csv         (~8000 rows)

Usage:
    python scripts/generate_sample_data.py
    python scripts/generate_sample_data.py --rows 5000  (larger dataset)
"""

import sys
import argparse
import random
import uuid
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pandas as pd
import numpy as np

# ── Project root setup ───────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
OUTPUT_DIR = PROJECT_ROOT / "data" / "sample"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Random seed for reproducibility ──────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# ── Reference data ────────────────────────────────────────
CITIES = [
    ("Mumbai",      "MH",  19.076,  72.877),
    ("Delhi",       "DL",  28.613,  77.209),
    ("Bangalore",   "KA",  12.972,  77.594),
    ("Chennai",     "TN",  13.082,  80.270),
    ("Kolkata",     "WB",  22.573,  88.364),
    ("Hyderabad",   "TS",  17.385,  78.487),
    ("Pune",        "MH",  18.520,  73.856),
    ("Ahmedabad",   "GJ",  23.023,  72.572),
    ("Jaipur",      "RJ",  26.912,  75.787),
    ("Lucknow",     "UP",  26.847,  80.947),
    ("Surat",       "GJ",  21.195,  72.830),
    ("Nagpur",      "MH",  21.145,  79.088),
    ("Indore",      "MP",  22.719,  75.857),
    ("Bhopal",      "MP",  23.259,  77.413),
    ("Chandigarh",  "PB",  30.733,  76.779),
    ("Coimbatore",  "TN",  11.017,  76.955),
    ("Visakhapatnam","AP", 17.686,  83.218),
    ("Kochi",       "KL",  9.931,   76.267),
    ("Patna",       "BR",  25.594,  85.137),
    ("Bhubaneswar", "OD",  20.296,  85.825),
]

CARRIERS = ["BlueDart", "DTDC", "Delhivery", "Ecom Express",
            "XpressBees", "Shadowfax", "FedEx India", "DHL India"]

VEHICLE_TYPES = ["Truck", "Van", "Mini-Truck", "Rail", "Air Cargo"]

CATEGORIES = ["Electronics", "Clothing", "Food & Beverage", "Furniture",
              "Pharmaceuticals", "Automotive Parts", "Books", "FMCG",
              "Industrial Equipment", "Perishables"]

DELAY_REASONS = ["Traffic Congestion", "Weather Conditions", "Vehicle Breakdown",
                 "Customs Delay", "Road Closure", "Driver Shortage",
                 "High Shipment Volume", "Address Issue", "No Delay"]

WEATHER_CONDITIONS = ["Clear", "Rain", "Fog", "Storm", "Snow", "Cloudy", "Drizzle"]

CONGESTION_LEVELS = [1, 2, 3, 4, 5]  # 1=free flow, 5=gridlock


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Approximate great-circle distance between two lat/lon points (km)."""
    R = 6371.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    return round(2 * R * np.arcsin(np.sqrt(a)), 1)


def rand_datetime(start: datetime, days: int) -> datetime:
    return start + timedelta(
        days=random.uniform(0, days),
        hours=random.uniform(0, 24),
    )


# ═══════════════════════════════════════════════════════════
# 1. SHIPMENTS
# ═══════════════════════════════════════════════════════════
def generate_shipments(n: int = 2000) -> pd.DataFrame:
    """
    Generate n synthetic shipment records.
    Delay probability is influenced by distance, weather season, and carrier —
    making the ML signal realistic enough for a student project.
    """
    print(f"  Generating {n} shipment records...")
    start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    records = []

    for i in range(n):
        # Pick origin & destination (different cities)
        origin, dest = random.sample(CITIES, 2)
        o_city, o_state, o_lat, o_lon = origin
        d_city, d_state, d_lat, d_lon = dest

        distance = haversine_km(o_lat, o_lon, d_lat, d_lon)
        vehicle = random.choice(VEHICLE_TYPES)
        carrier = random.choice(CARRIERS)
        category = random.choice(CATEGORIES)
        weight = round(random.uniform(0.5, 2000.0), 2)

        scheduled_pickup = rand_datetime(start_date, 365)
        # Transit time: rough estimate based on distance & vehicle
        base_days = distance / 500 if vehicle != "Air Cargo" else 0.5
        transit_hours = base_days * 24 * random.uniform(0.8, 1.2)
        scheduled_delivery = scheduled_pickup + timedelta(hours=transit_hours)

        # ── Delay logic (synthetic but correlated with features) ──
        delay_prob = 0.25  # base 25% delay rate
        if distance > 1500:
            delay_prob += 0.10
        if vehicle == "Truck":
            delay_prob += 0.08
        if category in ("Perishables", "Pharmaceuticals"):
            delay_prob += 0.05
        if scheduled_pickup.month in (6, 7, 8):  # monsoon
            delay_prob += 0.12
        if carrier in ("Shadowfax", "Ecom Express"):
            delay_prob += 0.03

        is_delayed = int(random.random() < min(delay_prob, 0.75))

        if is_delayed:
            delay_minutes = round(random.expovariate(1 / 180), 1)  # mean ~3h
            delay_minutes = min(delay_minutes, 2880)  # cap at 48h
            actual_pickup = scheduled_pickup + timedelta(
                minutes=random.uniform(0, delay_minutes * 0.3)
            )
            actual_delivery = scheduled_delivery + timedelta(minutes=delay_minutes)
            reason_pool = [r for r in DELAY_REASONS if r != "No Delay"]
            delay_reason = random.choice(reason_pool)
        else:
            delay_minutes = 0.0
            actual_pickup = scheduled_pickup + timedelta(minutes=random.uniform(-30, 30))
            actual_delivery = scheduled_delivery + timedelta(minutes=random.uniform(-60, 60))
            delay_reason = "No Delay"

        status = "Delivered" if actual_delivery < datetime.now(timezone.utc) else "In Transit"

        records.append({
            "shipment_id":          f"SHP-{scheduled_pickup.strftime('%Y%m%d')}-{i+1:04d}",
            "origin_city":          o_city,
            "origin_state":         o_state,
            "origin_lat":           o_lat,
            "origin_lon":           o_lon,
            "destination_city":     d_city,
            "destination_state":    d_state,
            "destination_lat":      d_lat,
            "destination_lon":      d_lon,
            "distance_km":          distance,
            "vehicle_type":         vehicle,
            "carrier":              carrier,
            "weight_kg":            weight,
            "category":             category,
            "scheduled_pickup":     scheduled_pickup.isoformat(),
            "actual_pickup":        actual_pickup.isoformat(),
            "scheduled_delivery":   scheduled_delivery.isoformat(),
            "actual_delivery":      actual_delivery.isoformat(),
            "is_delayed":           is_delayed,
            "delay_minutes":        delay_minutes,
            "delay_reason":         delay_reason,
            "status":               status,
            "data_source":          "SYNTHETIC — generated by generate_sample_data.py",
        })

    df = pd.DataFrame(records)
    print(f"    Delay rate: {df['is_delayed'].mean():.1%}")
    return df


# ═══════════════════════════════════════════════════════════
# 2. TRAFFIC
# ═══════════════════════════════════════════════════════════
def generate_traffic(n: int = 3000) -> pd.DataFrame:
    """Generate synthetic traffic condition records for major routes."""
    print(f"  Generating {n} traffic records...")
    start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    routes = [
        f"{CITIES[i][0][:3].upper()}-{CITIES[j][0][:3].upper()}-NH{random.randint(1,100)}"
        for i in range(len(CITIES))
        for j in range(i + 1, len(CITIES))
    ][:40]  # limit to 40 routes

    records = []
    for i in range(n):
        ts = rand_datetime(start_date, 365)
        hour = ts.hour
        # Rush hours: 7-10am, 5-8pm → higher congestion
        if 7 <= hour <= 10 or 17 <= hour <= 20:
            congestion = random.choices(CONGESTION_LEVELS, weights=[5, 15, 30, 35, 15])[0]
        elif 0 <= hour <= 5:
            congestion = random.choices(CONGESTION_LEVELS, weights=[50, 30, 15, 4, 1])[0]
        else:
            congestion = random.choices(CONGESTION_LEVELS, weights=[20, 30, 30, 15, 5])[0]

        base_speed = 80 - (congestion - 1) * 15
        avg_speed = round(max(5, base_speed + random.gauss(0, 8)), 1)
        incident = int(congestion >= 4 and random.random() < 0.25)

        records.append({
            "record_id":        f"TRF-{i+1:05d}",
            "route_id":         random.choice(routes),
            "timestamp":        ts.isoformat(),
            "congestion_level": congestion,
            "avg_speed_kmh":    avg_speed,
            "incident_flag":    incident,
            "data_source":      "SYNTHETIC",
        })

    return pd.DataFrame(records)


# ═══════════════════════════════════════════════════════════
# 3. WEATHER
# ═══════════════════════════════════════════════════════════
def generate_weather(n: int = 1500) -> pd.DataFrame:
    """Generate synthetic weather records for all cities."""
    print(f"  Generating {n} weather records...")
    start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    records = []

    for i in range(n):
        city_data = random.choice(CITIES)
        city, state, lat, _ = city_data
        ts = rand_datetime(start_date, 365)
        month = ts.month

        # Seasonal logic
        if month in (6, 7, 8, 9):   # monsoon
            condition = random.choices(
                WEATHER_CONDITIONS,
                weights=[5, 40, 10, 15, 0, 20, 10]
            )[0]
            temp = round(random.uniform(24, 35), 1)
            precip = round(random.uniform(0, 120), 1) if condition in ("Rain", "Storm", "Drizzle") else 0.0
        elif month in (12, 1, 2):   # winter
            condition = random.choices(
                WEATHER_CONDITIONS,
                weights=[30, 10, 25, 5, 5, 20, 5]
            )[0]
            temp = round(random.uniform(8, 22), 1)
            precip = round(random.uniform(0, 20), 1) if condition in ("Rain", "Drizzle") else 0.0
        else:                        # summer / spring
            condition = random.choices(
                WEATHER_CONDITIONS,
                weights=[45, 15, 5, 5, 0, 25, 5]
            )[0]
            temp = round(random.uniform(28, 44), 1)
            precip = round(random.uniform(0, 10), 1) if condition == "Rain" else 0.0

        wind = round(random.uniform(5, 80 if condition == "Storm" else 40), 1)
        visibility = round(
            random.uniform(0.5, 3.0) if condition in ("Fog", "Storm")
            else random.uniform(5.0, 20.0), 1
        )

        records.append({
            "record_id":        f"WTH-{i+1:05d}",
            "city":             city,
            "state":            state,
            "timestamp":        ts.isoformat(),
            "condition":        condition,
            "temperature_c":    temp,
            "wind_speed_kmh":   wind,
            "visibility_km":    visibility,
            "precipitation_mm": precip,
            "data_source":      "SYNTHETIC",
        })

    return pd.DataFrame(records)


# ═══════════════════════════════════════════════════════════
# 4. GPS TRACKS
# ═══════════════════════════════════════════════════════════
def generate_gps(shipments_df: pd.DataFrame, points_per_shipment: int = 4) -> pd.DataFrame:
    """
    Generate synthetic GPS waypoints for each shipment.
    Waypoints are linearly interpolated between origin and destination.
    """
    n_total = len(shipments_df) * points_per_shipment
    print(f"  Generating ~{n_total} GPS records ({points_per_shipment} pts/shipment)...")
    records = []

    for _, row in shipments_df.iterrows():
        o_lat, o_lon = row["origin_lat"],      row["origin_lon"]
        d_lat, d_lon = row["destination_lat"], row["destination_lon"]

        try:
            pickup_dt = datetime.fromisoformat(row["actual_pickup"])
            delivery_dt = datetime.fromisoformat(row["actual_delivery"])
        except Exception:
            continue

        total_seconds = max((delivery_dt - pickup_dt).total_seconds(), 3600)

        for step in range(points_per_shipment):
            frac = step / max(points_per_shipment - 1, 1)
            ts = pickup_dt + timedelta(seconds=frac * total_seconds)
            lat = round(o_lat + frac * (d_lat - o_lat) + random.gauss(0, 0.05), 6)
            lon = round(o_lon + frac * (d_lon - o_lon) + random.gauss(0, 0.05), 6)
            speed = round(random.uniform(0 if frac in (0, 1) else 20, 90), 1)
            heading = round(
                np.degrees(np.arctan2(d_lon - o_lon, d_lat - o_lat)) % 360, 1
            )

            records.append({
                "record_id":    f"GPS-{row['shipment_id']}-{step+1:02d}",
                "shipment_id":  row["shipment_id"],
                "timestamp":    ts.isoformat(),
                "latitude":     lat,
                "longitude":    lon,
                "speed_kmh":    speed,
                "heading_degrees": heading,
                "data_source":  "SYNTHETIC",
            })

    return pd.DataFrame(records)


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic sample datasets (clearly labelled as SYNTHETIC)"
    )
    parser.add_argument("--rows", type=int, default=2000,
                        help="Number of shipment rows to generate (default: 2000)")
    args = parser.parse_args()

    print("=" * 60)
    print("  SYNTHETIC SAMPLE DATA GENERATOR")
    print("  ⚠️  All data is SYNTHETIC — not real logistics data")
    print("=" * 60)

    shipments_df = generate_shipments(args.rows)
    traffic_df   = generate_traffic(int(args.rows * 1.5))
    weather_df   = generate_weather(int(args.rows * 0.75))
    gps_df       = generate_gps(shipments_df, points_per_shipment=4)

    files = {
        "sample_shipments.csv": shipments_df,
        "sample_traffic.csv":   traffic_df,
        "sample_weather.csv":   weather_df,
        "sample_gps.csv":       gps_df,
    }

    print("\n  Saving files to data/sample/:")
    for filename, df in files.items():
        path = OUTPUT_DIR / filename
        df.to_csv(path, index=False)
        kb = path.stat().st_size / 1024
        print(f"    ✓ {filename:30s}  {len(df):6,} rows  {kb:7.1f} KB")

    print(f"\n  Delay rate in shipments: {shipments_df['is_delayed'].mean():.1%}")
    print(f"  Date range: 2023-01-01 to 2023-12-31")
    print("\n  ✅ Sample data generation complete.")
    print("  Replace with real data from:")
    print("    https://www.kaggle.com/datasets/prachi13/customer-logistics-data")


if __name__ == "__main__":
    main()

