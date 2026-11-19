# University Review & Viva Voce Demonstration Guide

**Project Title:** Big Data Classification and Prediction for Transportation and Logistics using Apache Hive  
**Course:** Big Data Technologies (BDT)  

---

## 🎯 6-Minute Live Demonstration Walkthrough for Evaluators

### Step 1: Open Application & Header Diagnostics
1. Open your browser and navigate to:  
   👉 **`http://localhost:5050`**
2. Point out the top header diagnostic badges:
   - `Hive: CONNECTED` (Shows Apache Hive data warehouse and Metastore connectivity)
   - `Storage: LOCAL / HDFS` (Tiered data lake storage abstraction)
   - `Spark: local[*]` (In-memory execution utilizing host CPU cores)
3. Point out the top official banner: **"Big Data Classification and Prediction for Transportation and Logistics using Apache Hive"**

### Step 2: Overview & Live KPIs (`/`)
1. Show the **Real-Time KPI Cards**:
   - Total Shipments (14,000+ records)
   - On-Time Deliveries (Green)
   - Delayed Shipments (Red)
   - Global Delay Percentage (~33.4%)
   - Mean Delay Duration (~176 mins)
   *(Explain to the evaluator: "All figures are computed dynamically from the Big Data warehouse without hardcoded values!")*
2. Highlight the interactive Chart.js visualizations:
   - Transportation Mode Volumes & Proportions
   - Carrier Delay Comparative Rates
   - Recent Dispatches Telemetry

### Step 3: Apache Hive Analytics & HiveQL Console (`/hive-page`) ⭐ *Central Module Demo*
1. Show the dedicated **Apache Hive Analytics** panel.
2. Click any of the **Quick-Run HiveQL Query Cards**:
   - `02_ontime_vs_delayed.hql` (Classifies On-Time vs Delayed with percentages)
   - `05_routes_highest_delays.hql` (Ranks top 15 bottleneck corridors with risk tier badges)
   - `06_transportation_mode_analysis.hql` (Compares Air, Ground, Rail, Sea)
3. Point out the real-time execution statistics:
   - Query execution duration in milliseconds (e.g., `Execution Time: 210 ms`).
   - Clean tabular output rendered dynamically.
4. Demonstrate running a **Custom HiveQL Query**:
   ```sql
   SELECT origin_city, COUNT(*) AS departures FROM shipments_orc GROUP BY origin_city ORDER BY departures DESC LIMIT 5
   ```
   Click **Execute HiveQL** and observe the live result table.
   *(Explain: "This executes genuine HiveQL over our partitioned ORC tables and Hive catalog!")*

### Step 4: Interactive Delay Prediction Simulator (`/predict-page`)
1. Enter pre-dispatch shipment parameters:
   - Origin: `Mumbai`, Destination: `Delhi`
   - Carrier: `BlueDart`, Vehicle: `Truck`
   - Distance: `1420 km`, Weight: `450 kg`
   - Departure Hour: `08:00` (Peak morning rush)
2. Click **⚡ Predict Delay Risk**:
   - Display the result: **Delayed** (High Risk, e.g., 78.4% delay probability).
   - Show the operational contributing factors (e.g., long-haul distance, peak hour departure).
   *(Explain: "Strict zero target leakage — no actual delivery times or delay durations are used during prediction!")*

### Step 5: Big Data Processing Console (`/processing-page`)
1. Highlight the processing actions for **Apache Hive**, **PySpark ETL**, and **Hadoop MapReduce**.
2. Click **Run MapReduce Job** to show streaming mapper and reducer execution across sorted keys.
3. Review the **Processing Jobs Audit History** table.

### Step 6: Model Evaluation & Benchmarks (`/model-page`)
1. Show the benchmark table comparing **Baseline (Logistic Regression)** vs. **Primary (Random Forest Classifier)**.
2. Point out:
   - Accuracy: **85.8%** vs 71.4%
   - ROC-AUC: **0.918** vs 0.771
3. Review the 2x2 Confusion Matrix and feature importance ranking.

---

## 🎓 Viva Voce Questions & Model Answers

#### Q1: What is Apache Hive and why is it used as the central Big Data technology here?
**Answer:** Apache Hive is an enterprise distributed data warehouse software built on top of the Apache Hadoop ecosystem. It provides a declarative SQL-like interface called **HiveQL** that allows developers to query, summarize, and analyze petabytes of structured and semi-structured data stored in HDFS. In our project, Hive acts as the central warehouse managing table schemas via the Hive Metastore, storing data in partitioned columnar ORC format, and executing multi-dimensional analytical queries without requiring low-level MapReduce code.

#### Q2: What is the difference between an External Table and a Managed Table in Apache Hive?
**Answer:**
- **External Table (`shipments_raw`):** Hive manages only the table schema in the Metastore, while the data files reside at a specified external storage location (`LOCATION '/data/raw'`). If the table is dropped (`DROP TABLE`), only metadata is deleted; the underlying raw data files remain safe.
- **Managed Table (`shipments_orc`):** Hive owns both the table schema and the physical data stored inside Hive's warehouse directory (`bigdata/hive/warehouse/`). If a managed table is dropped, Hive deletes both the metadata and the data files.

#### Q3: Why did you choose the ORC (Optimized Row Columnar) file format with Snappy compression?
**Answer:** ORC is specifically optimized for high-performance Big Data queries in Hive. Unlike row-oriented CSV or Text files:
1. **Columnar Storage:** Only the columns required by a query (e.g., `is_delayed`, `distance_km`) are read from disk, drastically minimizing I/O.
2. **Built-in Indexes:** ORC stores lightweight indexes (min/max/sum) at stripe level (every 64MB-256MB) and row group level (every 10,000 rows), enabling predicate pushdown.
3. **High Compression:** Combining dictionary encoding with Snappy compression reduced raw storage size by **~67.5%** with minimal CPU decompression overhead.

#### Q4: How does dynamic partitioning by `transportation_mode` improve query performance?
**Answer:** In Hive, partitioning physically segregates data into subdirectories on disk (e.g., `/transportation_mode=Air/`, `/transportation_mode=Ground/`). When a query specifies `WHERE transportation_mode = 'Air'`, Hive applies **partition pruning**—reading only that specific subdirectory and skipping all other modes. This reduces disk I/O and query latency by up to 75%.

#### Q5: What is target leakage in machine learning and how did you prevent it?
**Answer:** Target leakage occurs when features included during training contain information about the target variable that would not be available at the actual moment of prediction in real-world deployment. In logistics delay prediction, using `actual_delivery_date`, `actual_pickup_date`, `delay_minutes`, or `delay_reason` would be fatal leakage because those attributes are only known *after* transit concludes. We strictly engineered our feature pipeline using only pre-dispatch attributes (origin, destination, carrier, vehicle, distance, weight, category, and scheduled departure hour/day/month).

#### Q6: How do Apache Hive, Spark, and MapReduce collaborate in this system?
**Answer:**
1. **Apache Hive:** Central warehouse for structured storage, Metastore schema catalog, ORC columnar storage, and declarative HiveQL analytical reporting.
2. **Apache Spark (PySpark):** Scalable in-memory distributed ETL engine that performs data deduplication, schema casting, and missing value imputation before loading into Hive.
3. **Hadoop Streaming MapReduce:** Foundational batch processing engine demonstrating low-level key-value mapping and shuffle-and-sort reduction across route, carrier, and vehicle dimensions.

#### Q7: Why does the web server run on port 5050 instead of port 5000?
**Answer:** On modern macOS operating systems (including Apple Silicon M-series Macs), the default AirPlay Receiver and ControlCenter system daemons bind to port 5000. Configuring `FLASK_PORT=5050` in `.env` avoids socket collision (`OSError: [Errno 48] Address already in use`) and guarantees immediate, conflict-free startup.
