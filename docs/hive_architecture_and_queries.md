# Apache Hive Architecture & HiveQL Queries

**Project Title:** Big Data Classification and Prediction for Transportation and Logistics using Apache Hive

---

### 1. Architectural Overview of Apache Hive in the Project

Apache Hive is the **central Big Data technology** in this architecture. It operates as the distributed data warehouse system built on top of the Hadoop ecosystem, enabling data summarization, ad-hoc querying, and analysis of large logistics datasets.

```
+-----------------------------------------------------------------------------------+
|                        APACHE HIVE DATA WAREHOUSE STACK                           |
+-----------------------------------------------------------------------------------+
|  QUERY INTERFACE   | Declarative HiveQL (Executed via CLI, Scripts, or Web UI)    |
+--------------------+--------------------------------------------------------------+
|  CATALOG/METASTORE | Hive Metastore (Table Schemas, Column Types, Partitions)     |
+--------------------+--------------------------------------------------------------+
|  EXECUTION ENGINE  | Spark Engine with enableHiveSupport() / MapReduce / Tez      |
+--------------------+--------------------------------------------------------------+
|  STORAGE FORMATS   | TextFile (External Staging) -> ORC (Managed Columnar Store)  |
|                    | Snappy Block Compression + Dynamic Partitioning by Mode      |
+--------------------+--------------------------------------------------------------+
|  STORAGE LAYER     | Hadoop Distributed File System (HDFS) / Local Warehouse      |
+-----------------------------------------------------------------------------------+
```

---

### 2. Hive Data Definition Language (DDL) Scripts

Located in `bigdata/hive/scripts/`:

#### Script 1: Database & Table Creation (`01_create_database_and_tables.hql`)
1. Creates the database `transportation_logistics_db`.
2. Creates external staging table `shipments_raw` using CSV SerDe.
3. Creates managed table `shipments_orc` stored as ORC, compressed with Snappy, and partitioned by `transportation_mode` (`Air`, `Ground`, `Rail`, `Sea`).
4. Creates reporting table `route_delay_summary`.

#### Script 2: Dynamic Partition Ingestion (`02_load_data.hql`)
Enables dynamic partition mode in Hive:
```sql
SET hive.exec.dynamic.partition = true;
SET hive.exec.dynamic.partition.mode = nonstrict;

INSERT OVERWRITE TABLE transportation_logistics_db.shipments_orc
PARTITION (transportation_mode)
SELECT
    shipment_id,
    origin_city,
    origin_state,
    origin_lat,
    origin_lon,
    destination_city,
    destination_state,
    destination_lat,
    destination_lon,
    distance_km,
    vehicle_type,
    carrier,
    weight_kg,
    category,
    CAST(scheduled_pickup AS TIMESTAMP),
    CAST(actual_pickup AS TIMESTAMP),
    CAST(scheduled_delivery AS TIMESTAMP),
    CAST(actual_delivery AS TIMESTAMP),
    status,
    is_delayed,
    delay_minutes,
    delay_reason,
    delivery_duration_hours,
    traffic_condition,
    weather_condition,
    transportation_mode
FROM transportation_logistics_db.shipments_raw;
```

---

### 3. The 7 Canonical HiveQL Analytics Queries

Located in `bigdata/hive/queries/`:

#### Query 01: Total Shipments Count (`01_total_shipments.hql`)
- **Objective:** Measure total warehouse record count across all partitions.
```sql
SELECT 
    COUNT(*) AS total_shipments,
    COUNT(DISTINCT origin_city) AS unique_origin_cities,
    COUNT(DISTINCT destination_city) AS unique_destination_cities,
    COUNT(DISTINCT carrier) AS total_carriers
FROM transportation_logistics_db.shipments_orc;
```
- **Big Data Mechanism:** Performs metadata lookup and distributed row counting.

#### Query 02: On-Time vs Delayed Classification (`02_ontime_vs_delayed.hql`)
- **Objective:** Classify historical shipments into On-Time vs Delayed categories, computing absolute counts and percentage shares.
```sql
SELECT 
    CASE 
        WHEN is_delayed = 1 THEN 'Delayed'
        ELSE 'On-Time'
    END AS shipment_classification,
    COUNT(*) AS shipment_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM transportation_logistics_db.shipments_orc
GROUP BY is_delayed;
```
- **Big Data Mechanism:** Evaluates CASE expressions, groups by binary target attribute, and uses window functions (`OVER ()`) to calculate distribution percentages in a single pass.

#### Query 03: Delay Percentage & Average Duration (`03_delay_percentage.hql`)
- **Objective:** Calculate the global network delay rate and the average duration of delayed shipments in minutes and hours.
```sql
SELECT 
    COUNT(*) AS total_shipments,
    SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) AS delayed_count,
    ROUND(SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS delay_percentage,
    ROUND(AVG(CASE WHEN is_delayed = 1 THEN delay_minutes ELSE NULL END), 2) AS avg_delay_minutes,
    ROUND(AVG(CASE WHEN is_delayed = 1 THEN delay_minutes ELSE NULL END) / 60.0, 2) AS avg_delay_hours
FROM transportation_logistics_db.shipments_orc;
```
- **Big Data Mechanism:** Vectorized column aggregation over numeric primitives.

#### Query 04: Average Delivery Duration by Mode (`04_avg_delivery_duration.hql`)
- **Objective:** Quantify the elapsed transit duration (hours and days) across transportation modes.
```sql
SELECT 
    transportation_mode,
    COUNT(*) AS total_shipments,
    ROUND(AVG(delivery_duration_hours), 2) AS avg_duration_hours,
    ROUND(AVG(delivery_duration_hours) / 24.0, 2) AS avg_duration_days,
    ROUND(MIN(delivery_duration_hours), 2) AS min_duration_hours,
    ROUND(MAX(delivery_duration_hours), 2) AS max_duration_hours
FROM transportation_logistics_db.shipments_orc
GROUP BY transportation_mode
ORDER BY avg_duration_hours ASC;
```
- **Big Data Mechanism:** Partition-level aggregation leveraging Hive's partition pruning.

#### Query 05: Top 15 Routes with Highest Delays (`05_routes_highest_delays.hql`)
- **Objective:** Pinpoint the highest-risk freight bottleneck corridors and assign risk tiers.
```sql
SELECT 
    origin_city,
    destination_city,
    transportation_mode,
    COUNT(*) AS total_shipments,
    SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) AS delayed_shipments,
    ROUND(SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS route_delay_percentage,
    ROUND(AVG(CASE WHEN is_delayed = 1 THEN delay_minutes ELSE 0 END), 1) AS avg_delay_minutes,
    CASE 
        WHEN (SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) >= 40.0 THEN 'HIGH_RISK'
        WHEN (SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) >= 25.0 THEN 'MEDIUM_RISK'
        ELSE 'LOW_RISK'
    END AS risk_tier
FROM transportation_logistics_db.shipments_orc
GROUP BY origin_city, destination_city, transportation_mode
HAVING COUNT(*) >= 20
ORDER BY delayed_shipments DESC, route_delay_percentage DESC
LIMIT 15;
```
- **Big Data Mechanism:** Multi-column grouping, HAVING predicate pushdown, and global sorting with LIMIT.

#### Query 06: Transportation Mode Comparative Analysis (`06_transportation_mode_analysis.hql`)
- **Objective:** Compare freight volume, delay rates, and haulage distance across all transportation modes.
```sql
SELECT 
    transportation_mode,
    COUNT(*) AS total_volume,
    SUM(CASE WHEN is_delayed = 0 THEN 1 ELSE 0 END) AS ontime_count,
    SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) AS delayed_count,
    ROUND(SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS mode_delay_rate,
    ROUND(AVG(distance_km), 2) AS avg_distance_km,
    ROUND(AVG(weight_kg), 2) AS avg_cargo_weight_kg
FROM transportation_logistics_db.shipments_orc
GROUP BY transportation_mode
ORDER BY total_volume DESC;
```

#### Query 07: Monthly Shipment Trends (`07_monthly_shipment_trends.hql`)
- **Objective:** Analyze monthly seasonal fluctuations in shipment volume and transit delay rates.
```sql
SELECT 
    date_format(scheduled_delivery, 'yyyy-MM') AS shipment_month,
    COUNT(*) AS monthly_volume,
    SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) AS delayed_count,
    SUM(CASE WHEN is_delayed = 0 THEN 1 ELSE 0 END) AS ontime_count,
    ROUND(SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS monthly_delay_percentage
FROM transportation_logistics_db.shipments_orc
WHERE scheduled_delivery IS NOT NULL
GROUP BY date_format(scheduled_delivery, 'yyyy-MM')
ORDER BY shipment_month ASC;
```

---

### 4. How Hive Queries Are Executed in This Project

1. **Via CLI Script:**
   ```bash
   python3 scripts/run_hive_queries.py
   ```
2. **Via Flask Web Dashboard:**
   Users can navigate to `/hive-page` to run any of the 7 queries with 1-click execution or write custom HiveQL statements in the web editor.
3. **Execution Runtime:**
   The backend service `backend/services/hive_service.py` executes HiveQL against the Hive Metastore and ORC tables using Spark's `enableHiveSupport()` engine and PyHive client, ensuring genuine Big Data execution without mocks or SQLite simulations.
