# Database Design & MongoDB Schema Specification

### 1. Database Overview
The application utilizes **MongoDB**, a distributed document-oriented NoSQL database. MongoDB was selected over traditional relational databases due to:
- **Flexible Schema-on-Read:** Easily ingests semi-structured telemetry without requiring ALTER TABLE schema migrations.
- **High-Velocity Document Writes:** Supports high-throughput ingestion of time-series GPS pings and weather observations.
- **Native Geospatial & Compound Indexing:** Provides fast B-tree and 2dsphere indexing for route and coordinate lookups.

---

### 2. Collection Specifications & Indexes

#### 1. Collection: `shipments`
Stores canonical freight shipment records.
```javascript
{
  "_id": ObjectId("..."),
  "shipment_id": "SHP-20230601-001",
  "origin_city": "Mumbai",
  "origin_state": "MH",
  "origin_lat": 19.076,
  "origin_lon": 72.877,
  "destination_city": "Delhi",
  "destination_state": "DL",
  "destination_lat": 28.613,
  "destination_lon": 77.209,
  "distance_km": 1420.5,
  "vehicle_type": "Truck",
  "carrier": "BlueDart",
  "weight_kg": 350.0,
  "category": "Electronics",
  "scheduled_pickup": "2023-06-01T08:00:00+00:00",
  "actual_pickup": "2023-06-01T08:45:00+00:00",
  "scheduled_delivery": "2023-06-03T18:00:00+00:00",
  "actual_delivery": "2023-06-04T02:30:00+00:00",
  "is_delayed": 1,
  "delay_minutes": 510.0,
  "delay_reason": "Traffic Congestion",
  "status": "Delivered",
  "source_file": "sample_shipments.csv",
  "ingested_at": "2023-06-01T00:00:00+00:00"
}
```
**Indexes:**
- `{ shipment_id: 1 }` (Unique)
- `{ origin_city: 1, destination_city: 1 }` (Route Queries)
- `{ is_delayed: 1 }` (Filtering)
- `{ scheduled_delivery: -1 }` (Timeline sorting)

#### 2. Collection: `traffic_records`
Stores road segment congestion levels.
```javascript
{
  "_id": ObjectId("..."),
  "record_id": "TRF-00001",
  "route_id": "MUM-DEL-NH48",
  "timestamp": "2023-06-01T08:30:00+00:00",
  "congestion_level": 4, // 1=Free flow, 5=Gridlock
  "avg_speed_kmh": 28.5,
  "incident_flag": 0
}
```
**Indexes:** `{ route_id: 1, timestamp: -1 }`

#### 3. Collection: `weather_records`
Stores meteorological observations.
```javascript
{
  "_id": ObjectId("..."),
  "record_id": "WTH-00001",
  "city": "Mumbai",
  "timestamp": "2023-06-01T08:00:00+00:00",
  "condition": "Rain",
  "temperature_c": 28.5,
  "wind_speed_kmh": 42.0,
  "visibility_km": 2.5,
  "precipitation_mm": 45.0
}
```
**Indexes:** `{ city: 1, timestamp: -1 }`

#### 4. Collection: `prediction_results`
Logs real-time inference predictions for auditability.
```javascript
{
  "_id": ObjectId("..."),
  "shipment_id": "ADHOC",
  "predicted_at": "2026-11-18T08:00:00+00:00",
  "is_delayed_predicted": 1,
  "delay_probability": 0.7245,
  "confidence": 0.7245,
  "delay_risk": "High",
  "contributing_factors": [
    "Long-haul route distance (1420 km) increases transit vulnerability",
    "Departure scheduled during peak traffic hours (08:00)"
  ],
  "input_features": { ... }
}
```
**Indexes:** `{ predicted_at: -1 }`, `{ delay_risk: 1 }`

#### 5. Collection: `processing_jobs`
Audit trail of distributed job executions.
```javascript
{
  "_id": ObjectId("..."),
  "job_id": "spark-etl-8a2b3c4d",
  "job_type": "spark_etl",
  "status": "completed",
  "started_at": "2026-11-18T08:00:00+00:00",
  "completed_at": "2026-11-18T08:00:02+00:00",
  "details": {
    "raw_records": 2000,
    "duplicates_removed": 0,
    "final_records": 2000,
    "output_path": "data/processed/shipments_clean/clean_shipments.csv"
  }
}
```
**Indexes:** `{ job_id: 1 }` (Unique), `{ started_at: -1 }`

