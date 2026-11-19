# Existing vs. Proposed System Analysis

**Project Title:** Big Data Classification and Prediction for Transportation and Logistics using Apache Hive

---

### 1. Existing System Architecture & Constraints

Traditional logistics management systems (LMS) and enterprise resource planning (ERP) suites were designed prior to the emergence of distributed Big Data architectures.

| Dimension | Existing System | Operational & Architectural Impact |
|---|---|---|
| **Storage Architecture** | Centralized Relational Databases (MySQL, PostgreSQL, Oracle). | Fails to scale horizontally when storing time-series GPS telematics, multi-city weather logs, and high-volume shipment histories. Table locks and I/O bottlenecks degrade query performance. |
| **Data Warehousing** | Monolithic star-schema data marts on traditional RDBMS. | Lacks distributed columnar file formats (ORC/Parquet) and dynamic partition pruning; queries require expensive full-table scans. |
| **Data Processing** | Single-node stored procedures and sequential cron reporting jobs. | Exponential query slowdowns and memory crashes as data sizes expand from thousands to millions of shipment rows. |
| **Analytics Capability** | Descriptive / Historical reporting only ("How many shipments were delayed last month?"). | Purely reactive; supply chain managers cannot intervene to avert pending delivery delays before packages depart. |
| **Machine Learning** | Ad-hoc spreadsheet regressions or detached scripts often tainted with target leakage. | Models trained on post-dispatch variables (such as actual transit duration) yield artificially inflated test metrics that collapse in live operations. |

---

### 2. Proposed Big Data Architecture (Centered on Apache Hive)

The proposed system replaces monolithic relational components with a distributed, multi-tiered Big Data architecture where **Apache Hive** serves as the central data warehouse.

```
+-------------------------------------------------------------------------------+
|                        PROPOSED BIG DATA ARCHITECTURE                         |
+-------------------------------------------------------------------------------+
|  DATA SOURCES    | Multi-source Shipments, Traffic Logs, Weather, GPS Telematics  |
+------------------+------------------------------------------------------------+
|  INGESTION & ETL | Automated data cleaning, deduplication, timestamp parsing   |
|                  | Binary delay labeling (actual_delivery > scheduled_delivery)|
+------------------+------------------------------------------------------------+
|  CENTRAL WAREHOUSE| APACHE HIVE (transportation_logistics_db)                  |
|  & BIG DATA LAKE | - External Staging: shipments_raw                           |
|                  | - Columnar Managed: shipments_orc (Partitioned by mode)     |
|                  | - HDFS Storage Abstraction Layer (Tiered raw/clean/metrics) |
|                  | - Metastore with Snappy Compression & Predicate Pushdown    |
+------------------+------------------------------------------------------------+
|  ANALYTICS ENGINE| HiveQL Distributed Queries (Grouping, Filtering, Sorting)   |
|                  | - 7 Canonical queries for classification and route patterns |
|                  | - PySpark In-Memory DataFrame Processing & MapReduce Batch  |
+------------------+------------------------------------------------------------+
|  MACHINE         | Scikit-learn Classification Pipeline                        |
|  LEARNING        | - Random Forest Classifier (Primary - 85.8% Accuracy)       |
|                  | - Logistic Regression (Baseline Benchmark)                  |
|                  | - Zero Target Leakage Feature Pipeline                      |
+------------------+------------------------------------------------------------+
|  PRESENTATION    | Responsive Blue & White Web Dashboard (Flask + Chart.js)    |
|                  | - Dedicated Apache Hive Analytics Console                   |
|                  | - Real-time delay prediction simulator & shipment registry  |
+-------------------------------------------------------------------------------+
```

---

### 3. Comparative Advantage Matrix

| Feature | Existing System | Proposed Apache Hive BDT System |
|---|---|---|
| **Primary Big Data Engine**| None (Single-node RDBMS) | **Apache Hive (HiveQL, Metastore, Managed ORC Tables)** |
| **Storage Format** | Row-oriented relational tables | **Columnar ORC format with Snappy compression & partition pruning** |
| **Horizontal Scalability** | Limited by single-server hardware capacity | **Horizontally scalable across Hadoop/HDFS distributed clusters** |
| **Querying Mechanism** | Proprietary SQL on monolithic engine | **Declarative HiveQL queries executed across distributed splits** |
| **Data Partitioning** | Manual RDBMS range partitioning | **Dynamic partitioning by `transportation_mode` (`Air`, `Ground`, `Rail`, `Sea`)** |
| **Predictive Capability** | Absent (Static historical reporting) | **Supervised ML Classification (Random Forest: 85.8% accuracy, 0.918 AUC)** |
| **Target Leakage Control** | Uncontrolled | **Strict zero-target-leakage validation omitting post-dispatch fields** |
| **Operator Interface** | Cluttered legacy client software | **Modern, responsive Blue & White web dashboard with HiveQL query editor** |
