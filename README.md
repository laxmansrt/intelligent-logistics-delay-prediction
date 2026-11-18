# INTELLIGENT LOGISTICS DELAY PREDICTION USING BIG DATA ANALYTICS

[![BDT University Project](https://img.shields.io/badge/Subject-Big%20Data%20Technologies%20(BDT)-blue.svg)](#)
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-green.svg)](#)
[![Tests Passing](https://img.shields.io/badge/Tests-62%2F62%20Passing-brightgreen.svg)](#)
[![Frameworks](https://img.shields.io/badge/BigData-Hadoop%20%7C%20MapReduce%20%7C%20Spark-orange.svg)](#)
[![Database](https://img.shields.io/badge/Database-MongoDB%20%7C%20HDFS-brightgreen.svg)](#)

---

## 📌 Project Overview
**Intelligent Logistics Delay Prediction Using Big Data Analytics** is a comprehensive, production-grade university Big Data Technologies (BDT) project. It demonstrates real-world application of:
- **Distributed Big Data Storage**: Hadoop Distributed File System (HDFS) architecture with dual-mode storage abstraction (local fallback & native cluster integration).
- **Distributed Batch Analytics**: Apache Hadoop Streaming MapReduce (`shipment_mapper.py` and `shipment_reducer.py`) for route, carrier, and vehicle transit bottleneck aggregations.
- **In-Memory Distributed Processing**: Apache Spark / PySpark DataFrame pipelines for multi-stage ETL, deduplication, schema enforcement, and feature derivation.
- **Machine Learning & Predictive Intelligence**: Scikit-learn pipelines with zero target leakage, evaluating Baseline (Logistic Regression) vs Primary (Random Forest Classifier) to forecast delay probabilities, risk categories (Low, Medium, High), and contributing operational factors.
- **Full-Stack Web Intelligence Dashboard**: Modern responsive UI with Flask REST backend, Chart.js visualizations, live telemetry tables, and job execution consoles.

---

## 🏛️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                            WEB BROWSER (CLIENT)                              │
│         HTML5 / CSS3 / JavaScript / Chart.js Interactive Dashboard          │
└──────────────────────────────────────┬───────────────────────────────────────┘
                                       │ HTTP REST API
┌──────────────────────────────────────▼───────────────────────────────────────┐
│                           FLASK WEB BACKEND (API)                            │
│    Routes: /api/v1/shipments  /api/v1/predict  /api/v1/analytics  /api/v1/jobs│
└────────┬─────────────────┬───────────────────┬─────────────────┬─────────────┘
         │                 │                   │                 │
┌────────▼────────┐ ┌──────▼─────────┐ ┌───────▼────────┐ ┌──────▼────────────┐
│   MongoDB NoSQL │ │   ML Pipeline  │ │  Apache Spark  │ │ MapReduce Engine   │
│   Document DB   │ │ (Scikit-learn) │ │    (PySpark)   │ │ (Hadoop Streaming) │
│                 │ │                │ │                │ │                    │
│ - shipments     │ │ - Random Forest│ │ - Schema/ETL   │ │ - shipment_mapper  │
│ - traffic_recs  │ │ - Baseline LR  │ │ - Deduplication│ │ - shipment_reducer │
│ - weather_recs  │ │ - Risk Scoring │ │ - Route Aggreg │ │ - Shuffle & Sort   │
│ - gps_records   │ │ - Feature Imp. │ │ - Multi-dim KPI│ │ - 390+ dimension   │
│ - jobs & metrics│ │ - No Leakage   │ │ - Parquet/CSV  │ │   aggregations     │
└─────────────────┘ └────────────────┘ └────────────────┘ └────────────────────┘
                                       │
┌──────────────────────────────────────▼───────────────────────────────────────┐
│                      STORAGE ABSTRACTION LAYER (Dual Mode)                   │
│         LOCAL MODE: data/raw/ data/processed/ data/analytics/ (Mirrored)     │
│         HDFS MODE:  hdfs://localhost:9000/logistics/raw/ ...                 │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Guide (Run Locally)

The application is engineered to run seamlessly on a student's development machine (macOS / Linux / Windows) without paid cloud services or complex multi-node setups.

### 1. Prerequisites
- Python 3.10+
- Java 11+ (JRE/JDK)
- Optional: MongoDB Community Edition (`brew services start mongodb-community`)
  *Note: The app runs in local fallback mode if MongoDB or Hadoop are not yet started!*

### 2. Environment Setup
```bash
# Clone or navigate to the repository
cd BDT

# Copy configuration
cp .env.example .env

# Install dependencies
pip3 install -r requirements.txt --break-system-packages
```

### 3. Generate Sample Data & Train Model
```bash
# Generate 14,000+ multi-source records (Shipments, Traffic, Weather, GPS)
python3 scripts/generate_sample_data.py

# Train ML Models (Logistic Regression vs Random Forest)
python3 scripts/train_model.py

# Run Distributed Processing Jobs
python3 scripts/run_spark_job.py
python3 bigdata/mapreduce/run_mapreduce.py
```

### 4. Launch Web Application
```bash
python3 run.py
```
Open your browser and navigate to:
👉 **`http://localhost:5000`**

---

## 🧪 Comprehensive Test Suite (62/62 Tests Passing)
Execute the complete test battery across all modules:
```bash
python3 -m pytest tests/ -v
```
Output:
```text
tests/test_phase1_setup.py ......................                        [ 35%]
tests/test_phase2_ingestion.py ..........................                [ 77%]
tests/test_phase3_bigdata_ml.py ...............                          [100%]
======================= 62 passed in 32.22s ========================
```

---

## 📁 Repository Directory Structure

```
BDT/
├── run.py                          # Application entry point
├── requirements.txt                # Python package dependencies
├── .env.example                    # Environment configuration template
├── .gitignore                      # Git exclusion rules
│
├── backend/                        # Flask Web Application & REST APIs
│   ├── app.py                      # Application factory pattern
│   ├── config.py                   # Centralized configuration
│   ├── extensions.py               # Database initializers & client singletons
│   ├── routes/                     # Blueprint API endpoints
│   │   ├── health.py               # Liveness probe & system diagnostics
│   │   ├── upload.py               # CSV ingestion & storage endpoints
│   │   ├── shipments.py            # Filterable shipment registry & KPIs
│   │   ├── predict.py              # ML inference & model retraining APIs
│   │   ├── analytics.py            # Visualizations & distribution feeds
│   │   └── jobs.py                 # Spark & MapReduce execution triggers
│   ├── services/                   # Business Logic & Infrastructure wrappers
│   │   ├── storage_service.py      # Local / HDFS storage abstraction layer
│   │   ├── ingestion_service.py    # Multi-source validator & data cleaner
│   │   ├── spark_service.py        # PySpark ETL & analytical aggregations
│   │   ├── mapreduce_service.py    # MapReduce streaming manager
│   │   └── prediction_service.py   # Model inference & logging service
│   └── utils/                      # Shared helpers
│       ├── logger.py               # Console & rotating file logger
│       ├── response.py             # Standardized REST envelopes
│       └── validators.py           # Upload security & header checkers
│
├── bigdata/                        # Big Data Technologies Engine
│   ├── spark/                      # Apache Spark / PySpark
│   │   ├── spark_session.py        # SparkSession builder & memory configuration
│   │   ├── shipment_processor.py   # Distributed ETL, deduplication & cleaning
│   │   ├── route_analyzer.py       # Bottleneck risk aggregation
│   │   └── delay_aggregator.py     # Multi-dimensional KPI aggregations
│   └── mapreduce/                  # Apache Hadoop Streaming MapReduce
│       ├── shipment_mapper.py      # Intermediate key-value generator
│       ├── shipment_reducer.py     # Shuffle & Sort aggregation reducer
│       └── run_mapreduce.py        # Local pipe & Hadoop cluster runner
│
├── ml/                             # Machine Learning Pipeline
│   ├── feature_engineering.py      # Zero-leakage feature preparation
│   ├── train_model.py              # Logistic Regression vs Random Forest trainer
│   └── predict.py                  # Real-time inference & factor explainer
│
├── database/                       # MongoDB Storage Engine
│   ├── mongo_client.py             # Connection manager & stats reporter
│   ├── schemas.py                  # Document structure specifications
│   └── indexes.py                  # Query optimization & compound indexing
│
├── data/                           # Data Lake Storage Layer
│   ├── sample/                     # Bundled multi-source sample CSVs
│   ├── raw/                        # Upload landing directory (shipments, traffic, etc.)
│   ├── processed/                  # Cleaned Spark output datasets
│   ├── analytics/                  # Generated route & delay metrics
│   └── models/                     # Trained .joblib pipeline & metrics JSON
│
├── frontend/                       # Logistics Intelligence User Interface
│   ├── templates/                  # Jinja2 HTML5 responsive views
│   │   ├── base.html               # Sidebar layout & system status badges
│   │   ├── index.html              # Overview KPIs & Chart.js distributions
│   │   ├── shipments.html          # Registry with multi-column filtering & search
│   │   ├── predict.html            # Interactive delay prediction simulator
│   │   ├── analytics.html          # Route bottlenecks & carrier performance
│   │   ├── processing.html         # Big Data job console & execution log
│   │   ├── model.html              # Model benchmarks & confusion matrix
│   │   └── upload.html             # Multi-source CSV ingestion panel
│   └── static/                     # Assets
│       ├── css/main.css            # Dark-blue modern logistics theme
│       └── js/main.js              # Live telemetry & status polling
│
├── scripts/                        # Standalone CLI utilities
│   ├── generate_sample_data.py     # Multi-source dataset generator
│   ├── init_db.py                  # MongoDB index & collection initializer
│   ├── run_spark_job.py            # Standalone Spark execution script
│   └── train_model.py              # Standalone ML training script
│
├── tests/                          # Automated Pytest suite (62 tests)
│   ├── test_phase1_setup.py        # Architecture & configuration tests
│   ├── test_phase2_ingestion.py    # Storage & CSV ingestion tests
│   └── test_phase3_bigdata_ml.py   # MapReduce, Spark, ML & API tests
│
└── docs/                           # Comprehensive Academic Documentation
    ├── abstract.md                 # Project abstract
    ├── problem_statement.md        # Problem statement & motivation
    ├── objectives.md               # Specific academic objectives
    ├── existing_and_proposed_system.md # Comparative system study
    ├── literature_review.md        # Literature survey & foundations
    ├── requirements.md             # Hardware & software requirements
    ├── system_architecture.md      # Detailed architectural diagrams
    ├── data_flow_diagram.md        # DFD Level 0, Level 1, Level 2
    ├── use_case_diagram.md         # Actor and use case definitions
    ├── database_design.md          # MongoDB schema & ER design
    ├── module_descriptions.md      # Detailed breakdown of all modules
    ├── algorithms.md               # MapReduce, Spark Catalyst, Random Forest
    ├── implementation_steps.md     # Step-by-step reproduction steps
    ├── test_cases.md               # Test matrix and verification logs
    ├── results_and_limitations.md  # Experimental outcomes & boundaries
    ├── future_enhancements.md      # Roadmap & cloud scaling vision
    ├── conclusion.md               # Academic project conclusion
    └── demo_guide.md               # University evaluation walkthrough guide
```

---

## 📊 Key Big Data Concepts Demonstrated

| Concept | Implementation Details | Academic Value |
|---|---|---|
| **Distributed Storage (HDFS)** | HDFS directory structure mirrored locally; NameNode/DataNode abstractions in `storage_service.py` | Shows understanding of distributed block replication and fault tolerance. |
| **MapReduce Batch Processing** | Streaming Mapper (`shipment_mapper.py`) & Reducer (`shipment_reducer.py`) with Shuffle & Sort simulation | Demonstrates foundational key-value aggregation without third-party black boxes. |
| **Spark In-Memory Analytics** | PySpark DataFrame API with column casting, deduplication, and window functions | Demonstrates DAG execution, Catalyst optimizer, and partition scaling. |
| **Schema-on-Read Data Lake** | Multi-source raw files (CSV) ingested directly and structured dynamically upon analytical query | Contrast with traditional relational RDBMS schemas. |
| **Zero Target Leakage ML** | Exclusion of actual delivery times and delay durations; training strictly on dispatch-time features | Validates sound empirical machine learning methodology. |
| **NoSQL Document Database** | MongoDB collections for semi-structured GPS tracks, traffic conditions, and predictions | Highlights flexibility over rigid relational schemas for time-series telematics. |

---

## 📜 Academic Integrity & Data Disclosure
All pre-bundled datasets in `data/sample/` are **SYNTHETICALLY GENERATED** using empirical probability distributions to ensure zero privacy violations and predictable academic demonstration. They are clearly labelled as `SYNTHETIC` across all interfaces. Users can upload real-world open datasets (such as the DataCo Smart Supply Chain or Kaggle Logistics Callsets) using the `/upload-page` interface.

