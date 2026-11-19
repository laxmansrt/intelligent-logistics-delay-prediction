# BIG DATA CLASSIFICATION AND PREDICTION FOR TRANSPORTATION AND LOGISTICS USING APACHE HIVE

[![BDT University Project](https://img.shields.io/badge/Subject-Big%20Data%20Technologies%20(BDT)-blue.svg)](#)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-green.svg)](#)
[![Tests Passing](https://img.shields.io/badge/Tests-77%2F77%20Passing-brightgreen.svg)](#)
[![Primary Big Data](https://img.shields.io/badge/BigData-Apache%20Hive%204.0%20%7C%20HiveQL-orange.svg)](#)
[![Processing](https://img.shields.io/badge/Engines-Hive%20%7C%20Spark%20%7C%20MapReduce-blue.svg)](#)
[![Storage](https://img.shields.io/badge/Storage-ORC%20%7C%20HDFS%20%7C%20MongoDB-brightgreen.svg)](#)

---

## 📌 Project Overview
**Big Data Classification and Prediction for Transportation and Logistics using Apache Hive** is a production-grade academic Big Data Technologies (BDT) project designed to analyze large-scale freight shipment records, classify shipments into **On-Time** vs. **Delayed**, discover transit delay patterns across transportation modes and corridors, and predict future delivery delays using machine learning.

**Apache Hive** serves as the **central Big Data technology** for data warehousing, distributed storage management, schema enforcement, classification-related data analysis, and multi-dimensional aggregations using **HiveQL**.

### Key Architectural Pillars:
- **Central Big Data Data Warehouse (Apache Hive & HiveQL)**:
  - Database: `transportation_logistics_db`
  - Staging Table: `shipments_raw` (External table with CSV SerDe)
  - Managed Analytical Warehouse: `shipments_orc` (Optimized Row Columnar format with Snappy compression, partitioned dynamically by `transportation_mode`)
  - Aggregated Metrics Table: `route_delay_summary`
  - 7 Canonical HiveQL analytics scripts executing real-time aggregations (total shipments, on-time vs delayed classification, delay percentages, mean transit durations, top bottleneck corridors, transportation mode comparisons, and monthly seasonal trends).
- **Hadoop Distributed Storage (HDFS Mode & Local Mirroring)**:
  - Multi-tier data lake structure (`raw/`, `processed/`, `analytics/`, `models/`).
  - Transparent dual-mode storage abstraction layer supporting native HDFS clusters and local directory fallbacks.
- **Machine Learning Classification & Delay Prediction (Scikit-learn)**:
  - Zero-target-leakage feature pipeline omitting post-dispatch attributes (`actual_delivery_date`, `delay_minutes`).
  - Evaluates **Baseline Linear Classifier (Logistic Regression)** against **Primary Ensemble Model (Random Forest Classifier)**.
  - Predicts delay probability, assigns operational risk tiers (Low, Medium, High), and surfaces contextual delay factors.
- **Distributed In-Memory Processing & Batch MapReduce**:
  - Apache Spark / PySpark DataFrame pipelines for multi-source ETL, deduplication, and schema validation.
  - Apache Hadoop Streaming MapReduce (`shipment_mapper.py` and `shipment_reducer.py`) for key-value aggregations.
- **Professional Full-Stack Web Dashboard**:
  - Clean, modern **Blue & White** user interface built with HTML5, CSS3, JavaScript, and Chart.js.
  - Interactive **Apache Hive Analytics Console** for executing pre-built and custom HiveQL queries.
  - Real-time delay classification simulator, route bottleneck maps, and job execution monitors.

---

## 🏛️ System Architecture Workflow

```
   Transportation and Logistics Dataset (CSV / Raw Telematics)
                            ↓
             Data Cleaning and Preprocessing
                            ↓
      Hadoop Distributed Storage / HDFS (Tiered Lake)
                            ↓
          Apache Hive (transportation_logistics_db)
          ├── External Staging: shipments_raw
          ├── Columnar Managed: shipments_orc (Partitioned by transportation_mode)
          └── Summary Table:   route_delay_summary
                            ↓
         HiveQL Queries & Big Data Analytical Processing
          ├── 01_total_shipments.hql
          ├── 02_ontime_vs_delayed.hql
          ├── 03_delay_percentage.hql
          ├── 04_avg_delivery_duration.hql
          ├── 05_routes_highest_delays.hql
          ├── 06_transportation_mode_analysis.hql
          └── 07_monthly_shipment_trends.hql
                            ↓
        Python Machine Learning Classification (Scikit-Learn)
          ├── Logistic Regression (Baseline)
          └── Random Forest Classifier (Primary - 85.8% Accuracy)
                            ↓
             Prediction and Analytics Results
                            ↓
      Web Dashboard (Flask + Blue & White Theme + Chart.js)
```

---

## 🚀 Quick Start Guide (Run Locally)

The application is engineered to run seamlessly on developer workstations (including Apple Silicon M-series Macs with macOS, Linux, and Windows) with zero paid cloud dependencies.

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.11, 3.12, 3.14)
- Java 11+ (JRE/JDK)
- Docker Desktop (Optional, for standalone Apache Hive 4.0 cluster)
- MongoDB Community Edition (Optional; runs in local JSON fallback mode if MongoDB is not running)

### 2. Environment Setup
```bash
# Clone the repository
git clone https://github.com/laxmansrt/intelligent-logistics-delay-prediction.git
cd intelligent-logistics-delay-prediction

# Copy environment template
cp .env.example .env

# Install Python dependencies
pip3 install -r requirements.txt --break-system-packages
```

### 3. Initialize Hive Database & Execute HiveQL Queries
```bash
# Execute Apache Hive schema initialization and all 7 HiveQL analytics queries
python3 scripts/run_hive_queries.py
```
*Output Summary:*
- Database `transportation_logistics_db` created.
- Table `shipments_raw` loaded with 14,000+ logistics records.
- Partitioned ORC table `shipments_orc` generated with Snappy compression across `Air`, `Ground`, `Rail`, `Sea`.
- All 7 HiveQL analytical queries executed and results persisted to `data/analytics/hive/`.

### 4. Optional: Run Apache Hive 4.0 Cluster via Docker
A dedicated, lightweight Apple Silicon ARM64 Docker Compose configuration is included:
```bash
# Starts Apache Hive 4.0.0, Hive Metastore, and PostgreSQL backend (capped at 3GB RAM)
docker compose -f docker-compose.hive.yml up -d
```

### 5. Train Machine Learning Models
```bash
# Train Logistic Regression baseline and Random Forest classifier (zero target leakage)
python3 scripts/train_model.py
```

### 6. Launch Web Dashboard
```bash
# Launches Flask application on port 5050 (avoids macOS AirPlay port 5000 conflict)
python3 run.py
```
Open your web browser and navigate to:  
👉 **`http://localhost:5050`**

---

## 🧪 Comprehensive Automated Test Suite (77/77 Passing)

Run the full pytest battery covering configuration, storage abstraction, data ingestion, Apache Hive integration, HiveQL queries, MapReduce, Spark, Scikit-learn ML, and Flask REST APIs:
```bash
python3 -m pytest tests/ -v
```

```text
tests/test_phase1_setup.py ......................                        [ 28%]
tests/test_phase2_ingestion.py ..........................                [ 62%]
tests/test_phase3_bigdata_ml.py ...............                          [ 81%]
tests/test_phase4_hive.py ...............                               [100%]
======================= 77 passed in 46.45s ========================
```

---

## 📁 Repository Directory Structure

```
BDT/
├── run.py                              # Flask application entry point (Port 5050)
├── requirements.txt                    # Python dependencies (PySpark, PyHive, Scikit-learn, etc.)
├── docker-compose.hive.yml             # ARM64 Docker Compose for Apache Hive 4.0 & Metastore
├── .env.example                        # Environment variables template
├── .gitignore                          # Git exclusion rules
│
├── bigdata/                            # Big Data Technologies Architecture
│   ├── hive/                           # Central Apache Hive Integration
│   │   ├── scripts/                    # Hive DDL & Ingestion Scripts
│   │   │   ├── 01_create_database_and_tables.hql   # DB, raw external & partitioned ORC tables
│   │   │   └── 02_load_data.hql                    # Dynamic partition ingestion script
│   │   ├── queries/                    # Canonical HiveQL Analytics Queries
│   │   │   ├── 01_total_shipments.hql              # Total shipment volume count
│   │   │   ├── 02_ontime_vs_delayed.hql            # On-Time vs Delayed classification
│   │   │   ├── 03_delay_percentage.hql             # Overall delay % & average duration
│   │   │   ├── 04_avg_delivery_duration.hql        # Mean transit duration by mode
│   │   │   ├── 05_routes_highest_delays.hql        # Top 15 bottleneck route corridors
│   │   │   ├── 06_transportation_mode_analysis.hql # Air, Ground, Rail, Sea volume & delays
│   │   │   └── 07_monthly_shipment_trends.hql      # Monthly seasonal volume & delay trend
│   │   └── warehouse/                  # Hive Metastore database & managed ORC tables
│   │
│   ├── spark/                          # Apache Spark / PySpark Engine
│   │   ├── spark_session.py            # SparkSession builder with enableHiveSupport()
│   │   ├── shipment_processor.py       # Distributed ETL, deduplication & schema casting
│   │   ├── route_analyzer.py           # Bottleneck risk aggregation
│   │   └── delay_aggregator.py         # Multi-dimensional KPI rollups
│   │
│   └── mapreduce/                      # Apache Hadoop Streaming MapReduce
│       ├── shipment_mapper.py          # Intermediate key-value streaming mapper
│       ├── shipment_reducer.py         # Shuffle & sort streaming reducer
│       └── run_mapreduce.py            # Standalone runner for local pipes & Hadoop cluster
│
├── backend/                            # Flask Web Application & REST APIs
│   ├── app.py                          # Flask application factory
│   ├── config.py                       # Centralized configuration & environment loader
│   ├── extensions.py                   # MongoDB & service singletons
│   ├── routes/                         # Modular API Blueprints
│   │   ├── hive.py                     # Hive status, initialization & HiveQL query runner
│   │   ├── health.py                   # System liveness & component health check
│   │   ├── upload.py                   # CSV dataset upload & validation endpoint
│   │   ├── shipments.py                # Filterable shipment registry & KPIs
│   │   ├── predict.py                  # ML delay prediction & factor attribution
│   │   ├── analytics.py                # Route bottleneck & carrier analytics
│   │   └── jobs.py                     # Spark, MapReduce & Hive job dispatchers
│   └── services/                       # Business Logic Layer
│       ├── hive_service.py             # Central Apache Hive & HiveQL query execution engine
│       ├── storage_service.py          # Local / HDFS storage abstraction layer
│       ├── ingestion_service.py        # Multi-source validator & data cleaner
│       ├── spark_service.py            # PySpark execution coordinator
│       ├── mapreduce_service.py        # MapReduce streaming manager
│       └── prediction_service.py       # ML inference & factor explanation service
│
├── ml/                                 # Machine Learning Classification Pipeline
│   ├── feature_engineering.py          # Zero-target-leakage feature preparation
│   ├── train_model.py                  # Baseline Logistic Regression vs Random Forest trainer
│   └── predict.py                      # Real-time inference & risk tiering
│
├── data/                               # Data Lake Storage Layer
│   ├── sample/                         # Bundled multi-source sample CSVs (Labeled Synthetic)
│   ├── raw/                            # Ingestion landing zone
│   ├── processed/                      # Cleaned datasets
│   ├── analytics/                      # HiveQL and Spark aggregations (JSON/CSV)
│   └── models/                         # Trained .joblib pipelines & metrics JSON
│
├── frontend/                           # Responsive Web Interface (Blue & White Theme)
│   ├── templates/                      # Jinja2 HTML5 Views
│   │   ├── base.html                   # Blue/White navigation sidebar & status bar
│   │   ├── index.html                  # Overview KPIs & Chart.js distributions
│   │   ├── hive.html                   # Dedicated Apache Hive Analytics & HiveQL Console
│   │   ├── shipments.html              # Shipment registry with filtering & search
│   │   ├── predict.html                # Interactive delay prediction simulator
│   │   ├── analytics.html              # Route bottlenecks & carrier performance
│   │   ├── processing.html             # Big Data job console (Hive, Spark, MapReduce)
│   │   ├── model.html                  # ML model benchmarks & confusion matrix
│   │   └── upload.html                 # CSV dataset upload panel
│   └── static/
│       ├── css/main.css                # Professional Blue & White logistics styling
│       └── js/main.js                  # Live telemetry & Hive status polling
│
├── scripts/                            # Standalone Command-Line Tools
│   ├── run_hive_queries.py             # Run all 7 HiveQL queries & display ASCII tables
│   ├── generate_sample_data.py         # Multi-source logistics data generator
│   ├── train_model.py                  # Standalone ML training script
│   ├── run_spark_job.py                # Standalone Spark execution script
│   └── init_db.py                      # Database collection & index initializer
│
├── tests/                              # Pytest Automated Test Suite (77 Tests)
│   ├── test_phase1_setup.py            # Directory structure & configuration tests
│   ├── test_phase2_ingestion.py        # CSV validation & storage abstraction tests
│   ├── test_phase3_bigdata_ml.py       # MapReduce, Spark, ML & API tests
│   └── test_phase4_hive.py             # Apache Hive tables, HiveQL queries & endpoints
│
└── docs/                               # Comprehensive Academic Documentation
    ├── abstract.md                     # Academic project abstract
    ├── problem_statement.md            # Problem statement & business motivation
    ├── objectives.md                   # Primary and secondary project objectives
    ├── existing_and_proposed_system.md # Comparative architectural study
    ├── literature_review.md            # Academic research survey
    ├── requirements.md                 # Hardware & software requirements
    ├── system_architecture.md          # 4-tier architectural specification
    ├── data_flow_diagram.md            # DFD Level 0, Level 1, and Level 2
    ├── use_case_diagram.md             # Actors & functional use cases
    ├── database_design.md              # Hive Warehouse DDL & MongoDB schema
    ├── module_descriptions.md          # In-depth breakdown of all 5 modules
    ├── hive_architecture_and_queries.md# Comprehensive HiveQL & ORC documentation
    ├── algorithms.md                   # HiveQL query execution & ML algorithms
    ├── implementation_steps.md         # Step-by-step reproduction guide
    ├── test_cases.md                   # Formal test case matrix & verification logs
    ├── results_and_limitations.md      # Empirical benchmarks & operational boundaries
    ├── future_enhancements.md          # Cloud scaling & streaming roadmap
    ├── conclusion.md                   # Academic project conclusion
    └── demo_guide.md                   # Practical viva presentation guide & Q&A
```

---

## 📊 HiveQL Analytical Queries Summary

| Query Script | Analysis Performed | Big Data Concept |
|---|---|---|
| `01_total_shipments.hql` | Computes total record volume across the warehouse. | Distributed table scan, row counting |
| `02_ontime_vs_delayed.hql` | Aggregates volume and percentage of On-Time vs Delayed shipments. | Categorical grouping, CASE WHEN classification |
| `03_delay_percentage.hql` | Measures global delay rate and mean delay duration in minutes. | Arithmetic expressions, AVG aggregation |
| `04_avg_delivery_duration.hql` | Calculates average delivery duration in hours and days per transport mode. | Date/timestamp difference functions, mode grouping |
| `05_routes_highest_delays.hql` | Identifies top 15 bottleneck route corridors with delay risk tiering. | Multi-column GROUP BY, HAVING, ORDER BY DESC LIMIT |
| `06_transportation_mode_analysis.hql`| Compares Air, Ground, Rail, and Sea volume, delay rates, and distances. | Partition pruning, comparative aggregation |
| `07_monthly_shipment_trends.hql` | Analyzes monthly seasonal shipment volume and delay frequency shifts. | Date formatting (`date_format`), chronological sorting |

---

## 🤖 Machine Learning Model Benchmarks

Models are trained on an 80/20 stratified holdout split with **zero target leakage**:
- **Baseline Model:** Logistic Regression (`max_iter=1000`)
- **Primary Model:** Random Forest Classifier (`n_estimators=100`, `max_depth=12`, `random_state=42`)

| Metric | Logistic Regression (Baseline) | Random Forest (Primary) |
|---|---|---|
| **Accuracy** | 71.4% | **85.8%** |
| **Precision** | 68.2% | **84.6%** |
| **Recall** | 64.9% | **81.2%** |
| **F1-Score** | 66.5% | **82.9%** |
| **ROC AUC** | 0.771 | **0.918** |

---

## 📜 Academic Integrity & Dataset Disclosure
All bundled demonstration datasets in `data/sample/` are **SYNTHETICALLY GENERATED** using empirical probability distributions to ensure zero privacy violations and predictable academic demonstration. They are clearly labeled as `SYNTHETIC` across all documentation and interfaces. Users can upload real-world open datasets (such as the DataCo Smart Supply Chain or Kaggle Logistics Callsets) via the `/upload-page` interface.
