# Project Objectives

**Project Title:** Big Data Classification and Prediction for Transportation and Logistics using Apache Hive

---

### Primary Objective
To design, implement, and validate a comprehensive Big Data analytics and machine learning classification platform centered on **Apache Hive** that ingests multi-source transportation and logistics records, manages them in a distributed data warehouse, executes declarative HiveQL analytics to classify shipments into On-Time vs. Delayed and discover transit delay patterns, and trains predictive classification models to forecast delay likelihood before shipment departure.

---

### Specific Sub-Objectives

1. **Multi-Source Data Ingestion & Data Preprocessing:**
   - Develop automated ingestion pipelines for transportation records (shipments, traffic congestion levels, weather conditions, GPS telematics).
   - Implement data cleaning routines: missing value handling, deduplication, strong type casting, date-time formatting, and delivery duration calculations.
   - Reliably establish target binary classification labels (`Delayed` = 1 when `actual_delivery_date` > `scheduled_delivery_date`, `On-Time` = 0 otherwise).

2. **Central Apache Hive Data Warehousing & Integration:**
   - Configure a reproducible Apache Hive environment with Hive Metastore and HDFS storage support.
   - Create a dedicated transportation and logistics Hive database (`transportation_logistics_db`).
   - Define external staging tables (`shipments_raw`) and managed columnar tables (`shipments_orc`) with Snappy compression, partitioned dynamically by `transportation_mode` (`Air`, `Ground`, `Rail`, `Sea`).
   - Author, test, and document 7 canonical HiveQL queries performing multi-dimensional grouping, filtering, sorting, and aggregation.

3. **Distributed Big Data Storage (HDFS):**
   - Design a tiered data lake layout separating `raw/`, `processed/`, `analytics/`, and `models/`.
   - Implement a dual-mode storage abstraction layer supporting both native WebHDFS clusters and local directory mirroring for academic reproducibility.

4. **Distributed Processing Engines (Spark & MapReduce):**
   - Implement PySpark DataFrame jobs for scalable in-memory ETL, schema enforcement, and bottleneck route identification.
   - Implement Hadoop Streaming MapReduce (`shipment_mapper.py` and `shipment_reducer.py`) for foundational key-value batch aggregations.

5. **Machine Learning Delay Classification & Prediction:**
   - Engineer a zero-target-leakage feature pipeline strictly omitting post-dispatch attributes.
   - Train and benchmark a baseline model (Logistic Regression) against a primary ensemble model (Random Forest Classifier).
   - Evaluate model performance using Accuracy, Precision, Recall, F1-Score, and a 2x2 Confusion Matrix.
   - Generate operational delay risk tiers (Low, Medium, High) and explain top contributing factors for individual dispatches.

6. **Full-Stack Analytics Web Dashboard:**
   - Develop a professional, responsive web interface adhering to a modern **Blue & White** logistics theme.
   - Build a dedicated **Apache Hive Analytics Console** enabling users to execute pre-configured and custom HiveQL queries with real-time result tables.
   - Provide interactive dispatch delay risk simulators, shipment search registries, and distributed job execution monitors.
