# System Architecture Specification

### 1. Conceptual 4-Tier Architecture

The platform follows a layered, decoupled service architecture:

```
+=============================================================================+
|                          TIER 1: PRESENTATION TIER                          |
|  - HTML5 & Responsive CSS3 (Navy Logistics Theme)                           |
|  - Chart.js Visualizations (Doughnut, Horizontal/Vertical Bars)             |
|  - Asynchronous Dynamic DOM (Vanilla JS ES6+)                               |
+=============================================================================+
                                      ▲
                                      │ HTTP REST JSON / Multipart Form-Data
                                      ▼
+=============================================================================+
|                          TIER 2: APPLICATION BACKEND                        |
|  - Flask Application Factory (backend/app.py)                               |
|  - Modular API Blueprints:                                                  |
|    • /api/v1/health       • /api/v1/shipments     • /api/v1/predict         |
|    • /api/v1/analytics    • /api/v1/jobs          • /api/v1/upload          |
|  - Storage Abstraction Service (backend/services/storage_service.py)        |
+=============================================================================+
                                      ▲
                                      │ In-Memory Pipeline & Process Calls
                                      ▼
+=============================================================================+
|                      TIER 3: DISTRIBUTED PROCESSING & ML                    |
|  - Apache Spark / PySpark:                                                  |
|    • ShipmentProcessor (Deduplication, Imputation, Type Casting)             |
|    • RouteAnalyzer (Bottleneck Grouping & Delay Rates)                      |
|    • DelayAggregator (Multi-dimensional KPI Rollups)                        |
|  - Apache Hadoop Streaming MapReduce:                                       |
|    • shipment_mapper.py (Key-Value Intermediate Generation)                 |
|    • shipment_reducer.py (Shuffle-and-Sort Aggregation)                     |
|  - Machine Learning Pipeline:                                               |
|    • Scikit-learn Random Forest Classifier (n_estimators=100, max_depth=12) |
|    • Logistic Regression Baseline Benchmark                                 |
|    • Zero Target Leakage Feature Preprocessor                               |
+=============================================================================+
                                      ▲
                                      │ I/O Operations
                                      ▼
+=============================================================================+
|                         TIER 4: PERSISTENCE & DATA LAKE                     |
|  - Storage Abstraction Layer:                                               |
|    • Local Mirror: data/raw/ data/processed/ data/analytics/ data/models/   |
|    • Hadoop HDFS: hdfs://localhost:9000/logistics/                          |
|  - MongoDB Document Store:                                                  |
|    • shipments, traffic_records, weather_records, gps_records               |
|    • prediction_results, processing_jobs, model_metrics                     |
+=============================================================================+
```

---

### 2. Dual-Mode Storage Architecture
To fulfill university evaluation requirements on personal laptops while supporting enterprise Hadoop deployments:

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
           data/processed/                    Block Replication: 3x
           data/analytics/                    NameNode Metadata Server
```

