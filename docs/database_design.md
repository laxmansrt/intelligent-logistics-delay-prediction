# Database & Data Warehouse Design Specification

**Project Title:** Big Data Classification and Prediction for Transportation and Logistics using Apache Hive

---

### 1. Architectural Role of Storage Components

The platform employs a dual-database architecture:
1. **Apache Hive (Primary Big Data Warehouse):** Used for large-scale data warehousing, distributed schema-on-read, dynamic partitioning, high-compression columnar ORC storage, and analytical HiveQL queries.
2. **MongoDB / Local Store (Application Cache & Registry):** Used by the Flask web application for sub-millisecond point queries, fast search indexing, and real-time frontend pagination.

---

### 2. Apache Hive Data Warehouse Design

Database Name: **`transportation_logistics_db`**

#### 2.1 Staging External Table: `shipments_raw`
Receives ingested CSV files directly from the data lake storage layer without duplicating file storage.

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS transportation_logistics_db.shipments_raw (
    shipment_id          STRING,
    origin_city          STRING,
    origin_state         STRING,
    origin_lat           DOUBLE,
    origin_lon           DOUBLE,
    destination_city     STRING,
    destination_state    STRING,
    destination_lat      DOUBLE,
    destination_lon      DOUBLE,
    distance_km          DOUBLE,
    transportation_mode  STRING,
    vehicle_type         STRING,
    carrier              STRING,
    weight_kg            DOUBLE,
    category             STRING,
    scheduled_pickup     STRING,
    actual_pickup        STRING,
    scheduled_delivery   STRING,
    actual_delivery      STRING,
    status               STRING,
    is_delayed           INT,
    delay_minutes        DOUBLE,
    delay_reason         STRING,
    delivery_duration_hours DOUBLE,
    traffic_condition    STRING,
    weather_condition    STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/data/raw/shipments'
TBLPROPERTIES ("skip.header.line.count"="1");
```

#### 2.2 Managed Columnar Analytical Table: `shipments_orc`
Engineered for high-performance Big Data queries. Data is stored in **Optimized Row Columnar (ORC)** format with **Snappy compression** and **partitioned dynamically by `transportation_mode`** (`Air`, `Ground`, `Rail`, `Sea`).

```sql
CREATE TABLE IF NOT EXISTS transportation_logistics_db.shipments_orc (
    shipment_id             STRING,
    origin_city             STRING,
    origin_state            STRING,
    origin_lat              DOUBLE,
    origin_lon              DOUBLE,
    destination_city        STRING,
    destination_state       STRING,
    destination_lat         DOUBLE,
    destination_lon         DOUBLE,
    distance_km             DOUBLE,
    vehicle_type            STRING,
    carrier                 STRING,
    weight_kg               DOUBLE,
    category                STRING,
    scheduled_pickup        TIMESTAMP,
    actual_pickup           TIMESTAMP,
    scheduled_delivery      TIMESTAMP,
    actual_delivery         TIMESTAMP,
    status                  STRING,
    is_delayed              INT,
    delay_minutes           DOUBLE,
    delay_reason            STRING,
    delivery_duration_hours DOUBLE,
    traffic_condition       STRING,
    weather_condition       STRING
)
PARTITIONED BY (transportation_mode STRING)
STORED AS ORC
TBLPROPERTIES (
    "orc.compress"="SNAPPY",
    "orc.create.index"="true",
    "orc.stripe.size"="67108864"
);
```

**Benefits of Hive ORC Partitioning:**
- **Partition Pruning:** Queries targeting a specific mode (e.g., `WHERE transportation_mode = 'Air'`) read only the relevant partition directory, bypassing the rest.
- **Columnar Projection:** Analytical queries aggregating only `is_delayed` or `distance_km` skip reading unreferenced string fields from disk.
- **Vectorized Execution:** Processes batches of 1,024 rows in CPU cache, achieving 3x-8x speedups over row-oriented text storage.

#### 2.3 Pre-Aggregated Summary Table: `route_delay_summary`
Maintains pre-computed corridor metrics for rapid reporting.

```sql
CREATE TABLE IF NOT EXISTS transportation_logistics_db.route_delay_summary (
    origin_city         STRING,
    destination_city    STRING,
    transportation_mode STRING,
    total_shipments     BIGINT,
    delayed_shipments   BIGINT,
    delay_percentage    DOUBLE,
    avg_delay_minutes   DOUBLE,
    avg_duration_hours  DOUBLE
)
STORED AS ORC;
```

---

### 3. Application Registry (MongoDB NoSQL Schema)

#### Collection: `shipments`
```json
{
  "_id": "ObjectId('...')",
  "shipment_id": "SHP-20230601-001",
  "origin_city": "Mumbai",
  "destination_city": "Delhi",
  "transportation_mode": "Ground",
  "vehicle_type": "Truck",
  "carrier": "BlueDart",
  "distance_km": 1420.5,
  "weight_kg": 350.0,
  "category": "Electronics",
  "scheduled_delivery": "2023-06-03T18:00:00Z",
  "actual_delivery": "2023-06-04T02:30:00Z",
  "is_delayed": 1,
  "delay_minutes": 510.0,
  "delay_reason": "Traffic Congestion",
  "status": "Delivered"
}
```

**Indexes:**
- `{ shipment_id: 1 }` (Unique)
- `{ origin_city: 1, destination_city: 1 }` (Compound corridor search)
- `{ is_delayed: 1 }` (Filter On-Time vs Delayed)
- `{ scheduled_delivery: -1 }` (Timeline sorting)
