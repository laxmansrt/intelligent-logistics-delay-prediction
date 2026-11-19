# System Architecture Specification

**Project Title:** Big Data Classification and Prediction for Transportation and Logistics using Apache Hive

---

### 1. Conceptual 4-Tier Architecture

The system follows a decoupled, layered Big Data architecture where **Apache Hive** acts as the central data warehouse:

```
+=============================================================================+
|                          TIER 1: PRESENTATION TIER                          |
|  - HTML5 & Responsive CSS3 (Professional Blue & White Logistics Theme)       |
|  - Dedicated Apache Hive Analytics & HiveQL Query Console                   |
|  - Interactive Delay Prediction Simulator & Real-time Risk Meters          |
|  - Chart.js Dynamic Visualizations (Doughnuts, Stacked Bars, Trend Lines)   |
|  - Vanilla JavaScript ES6+ Async State Management                           |
+=============================================================================+
                                      ▲
                                      │ HTTP REST API (JSON)
                                      ▼
+=============================================================================+
|                          TIER 2: APPLICATION BACKEND                        |
|  - Flask Application Factory (backend/app.py - Port 5050)                   |
|  - Modular API Blueprints:                                                  |
|    • /api/v1/hive         • /api/v1/shipments     • /api/v1/predict         |
|    • /api/v1/analytics    • /api/v1/jobs          • /api/v1/upload          |
|    • /api/v1/health                                                         |
|  - Central Hive Service (backend/services/hive_service.py)                  |
|  - Storage Abstraction Layer (backend/services/storage_service.py)          |
+=============================================================================+
                                      ▲
                                      │ Query Execution & In-Memory Calls
                                      ▼
+=============================================================================+
|                 TIER 3: CENTRAL BIG DATA & ML PROCESSING TIER               |
|                                                                             |
|  [PRIMARY BIG DATA ENGINE: APACHE HIVE & HIVEQL]                            |
|  - transportation_logistics_db                                              |
|  - External Staging Table: shipments_raw (CSV SerDe)                        |
|  - Managed Columnar Table: shipments_orc (Snappy, Partitioned by Mode)      |
|  - 7 Canonical HiveQL Analytics Queries (Aggregations, Bottlenecks, Trends)  |
|                                                                             |
|  [AUXILIARY PROCESSING ENGINES]                                             |
|  - Apache Spark / PySpark: DataFrame ETL, Schema Enforcement, Window Groups   |
|  - Hadoop Streaming MapReduce: shipment_mapper.py & shipment_reducer.py     |
|                                                                             |
|  [MACHINE LEARNING CLASSIFICATION PIPELINE]                                 |
|  - Zero Target Leakage Preprocessing (Excludes actual delivery/delay time)  |
|  - Primary: Random Forest Classifier (n_estimators=100, max_depth=12)       |
|  - Baseline: Logistic Regression Linear Benchmark                           |
|  - Evaluation: Accuracy, Precision, Recall, F1-Score, Confusion Matrix      |
+=============================================================================+
                                      ▲
                                      │ I/O Operations & Persistence
                                      ▼
+=============================================================================+
|                     TIER 4: PERSISTENCE & DATA WAREHOUSE                    |
|  - Apache Hive Metastore & Warehouse:                                       |
|    • bigdata/hive/warehouse/ (ORC Partitions & Schema Catalog)              |
|  - Distributed Storage Abstraction Layer:                                   |
|    • Tiered Data Lake: raw/, processed/, analytics/, models/                |
|    • Local Mirroring Mode & Hadoop HDFS Integration Mode (WebHDFS)          |
|  - NoSQL Document Store (MongoDB Community / Fallback):                     |
|    • Fast index queries for shipments, traffic, weather, predictions, jobs  |
+=============================================================================+
```

---

### 2. Detailed Data Flow Workflow

```
   [1. Ingestion]           [2. Big Data Warehouse]       [3. Analytics & ML]      [4. Dashboard]
Raw Logistics Records   ──>  Apache Hive Staging    ──>  HiveQL Analytics     ──> Professional
(Shipments, Telematics)      Table (shipments_raw)       (7 Core Queries)         Blue & White
                                     │                                            Dashboard
                                     ▼                                                ▲
                             Columnar Managed Table  ──>  Scikit-Learn ML             │
                             (shipments_orc)              Classification Pipeline     │
                             Partitioned by Mode          (Random Forest Model) ──────┘
```

---

### 3. Dual-Mode Storage Architecture
To support reproducible execution on laptops while preserving distributed cluster compatibility:

```
                         StorageService.save_file()
                                      │
                     ┌────────────────┴────────────────┐
                     ▼                                 ▼
          [STORAGE_MODE == 'local']         [STORAGE_MODE == 'hdfs']
                     │                                 │
                     ▼                                 ▼
            Local Filesystem                   Apache WebHDFS REST API
            data/raw/shipments/                hdfs://namenode:9000/logistics/
            data/processed/                    Block Replication Factor: 3x
            data/analytics/                    NameNode Metadata Management
```
