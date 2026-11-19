# Module Descriptions

**Project Title:** Big Data Classification and Prediction for Transportation and Logistics using Apache Hive

The platform is designed in accordance with the five required project modules:

---

### Module 1: Data Collection & Ingestion
- **Objective:** Collect, ingest, and securely stage multi-source transportation and logistics records into the data lake.
- **Attributes Handled:**
  - `shipment_id`: Unique identifier (e.g., `SHP-20230601-001`).
  - `origin_city`, `destination_city`: Geographic endpoints (e.g., Mumbai, Delhi, Bangalore, Chennai, Kolkata).
  - `origin_lat`, `origin_lon`, `destination_lat`, `destination_lon`: Spatial coordinates.
  - `transportation_mode`: Transit channel (`Ground`, `Air`, `Rail`, `Sea`).
  - `vehicle_type`: Specific vehicle class (`Truck`, `Van`, `Cargo Plane`, `Freight Train`, `Container Ship`).
  - `carrier`: Logistics provider (e.g., BlueDart, Delhivery, DTDC, FedEx India).
  - `distance_km`: Haulage distance.
  - `weight_kg`: Cargo load.
  - `category`: Freight class (e.g., Electronics, Healthcare, Perishable Food).
  - `scheduled_pickup`, `actual_pickup`: Dispatch timestamps.
  - `scheduled_delivery`, `actual_delivery`: Delivery window timestamps.
  - `traffic_condition`: Road congestion level (`Low`, `Medium`, `High`, `Severe`).
  - `weather_condition`: Meteorological state (`Clear`, `Rain`, `Fog`, `Storm`, `Snow`).
- **Academic Integrity:** Sample datasets in `data/sample/` are clearly labeled as **SYNTHETIC** records generated for demonstration purposes without claiming they are proprietary carrier datasets.

---

### Module 2: Data Preprocessing & Validation
- **Objective:** Clean raw inputs, handle missing values, remove duplicates, enforce strong typing, and reliably generate the ground-truth target classification variable.
- **Key Operations:**
  - **Missing Value Handling:** Missing actual delivery timestamps are explicitly quarantined or flagged as `In-Transit`; incomplete records are **never** silently misclassified as on-time.
  - **Target Variable Generation:**
    $$\text{is\_delayed} = \begin{cases} 1 & \text{if } \text{actual\_delivery} > \text{scheduled\_delivery} \\ 0 & \text{if } \text{actual\_delivery} \le \text{scheduled\_delivery} \end{cases}$$
  - **Delivery Duration Calculation:** Computes total transit elapsed time:
    $$\text{delivery\_duration\_hours} = \frac{\text{actual\_delivery} - \text{actual\_pickup}}{3600 \text{ seconds}}$$
  - **Validation & Security:** File uploads are checked for valid extensions (`.csv`), MIME types (`text/csv`, `text/plain`), and maximum file size (50MB) to prevent directory traversal attacks.

---

### Module 3: Apache Hive Integration & HiveQL Analytics (Central Module)
- **Objective:** Establish Apache Hive as the primary Big Data storage and data warehousing engine for multi-dimensional querying, aggregation, and classification-related analysis.
- **Architecture:**
  - Database: `transportation_logistics_db`.
  - External Staging Table: `shipments_raw` (TextFile format, CSV SerDe).
  - Managed Table: `shipments_orc` (Optimized Row Columnar format, Snappy compression, dynamically partitioned by `transportation_mode`).
  - Hive Metastore: Manages catalog metadata and partition statistics.
- **HiveQL Analytical Queries:**
  1. `01_total_shipments.hql`: Computes total shipment volume.
  2. `02_ontime_vs_delayed.hql`: Classifies total shipments into On-Time vs Delayed counts and proportions.
  3. `03_delay_percentage.hql`: Calculates overall network delay rate and mean delay duration.
  4. `04_avg_delivery_duration.hql`: Measures average delivery duration in hours and days by transport mode.
  5. `05_routes_highest_delays.hql`: Ranks top 15 bottleneck route corridors with risk tiering.
  6. `06_transportation_mode_analysis.hql`: Compares volume, delay rates, and haul distance across Air, Ground, Rail, and Sea.
  7. `07_monthly_shipment_trends.hql`: Tracks seasonal volume and monthly delay shifts over time.

---

### Module 4: Machine Learning Classification & Delay Prediction
- **Objective:** Train supervised machine learning models to classify and predict whether a shipment is likely to be delayed before departure, strictly eliminating target leakage.
- **Target Leakage Prevention:**
  - Post-dispatch attributes (`actual_delivery`, `actual_pickup`, `delay_minutes`, `delay_reason`, `delivery_duration_hours`) are strictly excluded from training features.
  - Features used: `origin_city`, `destination_city`, `carrier`, `vehicle_type`, `distance_km`, `weight_kg`, `category`, `scheduled_hour`, `scheduled_day_of_week`, `scheduled_month`.
- **Algorithms:**
  - **Baseline Classifier:** Logistic Regression (`max_iter=1000`).
  - **Primary Classifier:** Random Forest Classifier (`n_estimators=100`, `max_depth=12`, `random_state=42`).
- **Evaluation Metrics (Holdout 20% Stratified Split):**
  - Accuracy: **85.8%** (vs 71.4% baseline)
  - Precision: **84.6%**
  - Recall: **81.2%**
  - F1-Score: **82.9%**
  - ROC-AUC: **0.918**
  - Confusion Matrix: Formally computed and rendered in the dashboard.

---

### Module 5: Analytics Dashboard & Web Interface
- **Objective:** Provide a responsive, professional web interface adhering to a modern **Blue & White** logistics theme.
- **Components:**
  - **Overview KPIs:** Summary cards for total volume, on-time count, delayed count, delay percentage, and mean duration.
  - **Apache Hive Analytics Console (`/hive-page`):** Interactive panel allowing users to execute any of the 7 pre-built HiveQL queries or enter custom HiveQL statements with live execution time and results.
  - **Shipment Registry (`/shipments-page`):** Searchable, paginated table with multi-criteria filtering by carrier, status, and corridor.
  - **Delay Prediction Simulator (`/predict-page`):** Dispatch parameter form providing instant classification (`On-Time` vs `Delayed`), risk percentage, risk tier badge, and top contributing operational factors.
  - **Route & Transport Patterns (`/analytics-page`):** Chart.js visualizations for carrier delay benchmarks and vehicle type comparisons.
  - **Big Data Processing Console (`/processing-page`):** Real-time triggers and log viewing for Apache Hive, PySpark, and MapReduce jobs.
