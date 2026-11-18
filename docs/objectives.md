# Project Objectives

### Primary Objective
To design, implement, and validate an intelligent logistics intelligence platform that leverages Big Data Technologies (Hadoop, MapReduce, Apache Spark, and MongoDB) and Machine Learning (Random Forest and Logistic Regression) to process multi-source freight data, identify operational delay bottlenecks, and predict shipment delays before departure.

---

### Specific Sub-Objectives

1. **Multi-Source Data Ingestion & Validation:**
   - Develop an extensible ingestion pipeline capable of parsing, validating, and cleaning heterogeneous datasets (shipment records, traffic levels, weather conditions, GPS telematics).
   - Enforce data security by validating MIME types, restricting file sizes to 50MB, and preventing directory traversal.

2. **Distributed Big Data Storage (HDFS):**
   - Design an HDFS tiered directory architecture separating `raw/`, `processed/`, `analytics/`, and `models/`.
   - Implement a transparent storage abstraction layer that supports both native HDFS WebHDFS clusters and local directory mirroring for local academic evaluation.

3. **Distributed Batch Analytics (MapReduce):**
   - Author custom MapReduce streaming algorithms (`shipment_mapper.py` and `shipment_reducer.py`) to aggregate delivery metrics across routes, carriers, and vehicle types without relying on black-box utilities.
   - Support both native cluster job submission via Hadoop Streaming JAR and local piping for developer environments.

4. **Scalable In-Memory Processing (Apache Spark / PySpark):**
   - Construct PySpark DataFrame ETL jobs to enforce strong typing, eliminate duplicate records, impute missing values, and extract temporal features (scheduled hour, day of week, month).
   - Execute Spark distributed aggregations to identify high-risk bottleneck transit corridors.

5. **Machine Learning Delay Prediction Pipeline:**
   - Build a reproducible feature engineering pipeline strictly omitting target leakage attributes (`actual_delivery`, `delay_minutes`, `delay_reason`).
   - Train and benchmark a baseline model (Logistic Regression) against an ensemble tree model (Random Forest Classifier).
   - Compute and log objective empirical metrics: Accuracy, Precision, Recall, F1-Score, and a 2x2 Confusion Matrix.
   - Formulate rule-assisted explanations to identify the primary factors contributing to delay risk for individual shipments.

6. **NoSQL Application Database (MongoDB):**
   - Design document schemas and create compound indexes for shipments, traffic records, weather observations, GPS tracks, predictions, and processing jobs.

7. **Interactive Web Dashboard:**
   - Construct a modern, responsive web application using Flask, HTML5, CSS3, JavaScript, and Chart.js featuring real-time KPI overview cards, shipment tracking tables, delay prediction calculators, route risk rankings, and big data job execution consoles.

