# Project Abstract

**Project Title:** Big Data Classification and Prediction for Transportation and Logistics using Apache Hive  
**Course:** Big Data Technologies (BDT)  
**Domain:** Big Data Warehousing, Distributed Data Engineering & Applied Machine Learning  

---

### Abstract

Freight transportation and logistics networks form the lifeblood of contemporary global commerce. However, transit unpredictability—stemmed from highway congestion, adverse weather, multi-modal transfer bottlenecks, and scheduling discrepancies—consistently induces delivery delays that inflate operational overheads and degrade customer reliability. Traditional logistics platforms rely on centralized relational database management systems (RDBMS) that buckle under the high velocity, volume, and variety of transportation telematics, such as GPS pings, multi-source transit events, and shipment lifecycle logs.

This project delivers an end-to-end Big Data Technologies platform titled **"Big Data Classification and Prediction for Transportation and Logistics using Apache Hive"**. The platform establishes **Apache Hive** as the central Big Data technology for distributed storage management, schema enforcement, data warehousing, and analytical classification, complemented by machine learning for proactive delay forecasting:

1. **Central Big Data Data Warehouse (Apache Hive & HiveQL):** Implements an enterprise-grade data warehouse in Apache Hive (`transportation_logistics_db`). Ingests raw logistics data into external staging tables (`shipments_raw`) and converts them into optimized, columnar managed tables (`shipments_orc`) with Snappy compression and dynamic partitioning by `transportation_mode` (`Air`, `Ground`, `Rail`, `Sea`). Employs declarative HiveQL scripts to perform multi-dimensional aggregations, classify shipments into On-Time vs. Delayed categories, evaluate transit duration patterns, and identify high-risk bottleneck transit corridors.
2. **Distributed Storage & Data Lake Architecture:** Implements a multi-tier data lake structure (`raw/`, `processed/`, `analytics/`, `models/`) with a dual-mode storage abstraction layer supporting native Hadoop Distributed File System (HDFS) and local directory mirroring for reproducible developer environments.
3. **Distributed In-Memory Processing & Batch MapReduce:** Utilizes Apache Spark (PySpark) DataFrames for multi-source ETL, deduplication, and feature derivation, along with Apache Hadoop Streaming MapReduce (`shipment_mapper.py` and `shipment_reducer.py`) for foundational key-value batch aggregations.
4. **Machine Learning Classification & Prediction Pipeline:** Employs Scikit-learn with strict zero-target-leakage preprocessing to train and evaluate a Baseline Linear Classifier (Logistic Regression) against a Primary Ensemble Model (Random Forest Classifier). The model classifies whether a new shipment is likely to be delayed before departure, categorizes delay risk (Low, Medium, High), and surfaces contextual operational risk factors.
5. **Interactive Web Dashboard:** A professional, responsive web application engineered with Flask, HTML5, CSS3, JavaScript, and Chart.js featuring a clean **Blue & White** visual theme. The dashboard provides logistics operators with real-time KPI overview cards, an interactive Apache Hive Analytics console for running HiveQL queries, a shipment tracking registry, an interactive delay prediction simulator, and distributed job execution monitors.

The platform is designed for zero-cost, reproducible execution on commodity personal workstations (including Apple Silicon M4 macOS, Linux, and Windows), while maintaining full architectural fidelity with distributed enterprise Hadoop and Apache Hive clusters.
