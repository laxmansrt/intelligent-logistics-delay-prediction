# Literature Review & Theoretical Foundations

### 1. Introduction
The confluence of distributed computing, IoT telematics, and predictive modeling has transformed transportation research. This review synthesizes seminal academic contributions in distributed storage, batch computing, and machine learning applied to supply chain optimization.

---

### 2. Foundations of Distributed Big Data Storage (HDFS)
Ghemawat et al. (2003) introduced the Google File System (GFS), inspiring the open-source **Apache Hadoop Distributed File System (HDFS)** (Shvachko et al., 2010). HDFS is optimized for:
- Large files (gigabytes to terabytes) written once and read many times.
- Streaming data access patterns rather than random read/write access.
- Fault tolerance through software-level block replication (default 3x) across commodity DataNodes coordinated by a central NameNode metadata server.

In this project, HDFS concepts are implemented through a tiered storage architecture:
- `raw/`: Immutable landing zone preserving raw upload provenance.
- `processed/`: Strongly typed, deduplicated datasets cleansed by PySpark.
- `analytics/`: Aggregated performance metrics produced by MapReduce and Spark.

---

### 3. Distributed Batch Computation: MapReduce vs. Spark
Dean and Ghemawat (2004) formalized the **MapReduce** programming model:
$$\text{Map}: (k_1, v_1) \rightarrow \text{list}(k_2, v_2)$$
$$\text{Reduce}: (k_2, \text{list}(v_2)) \rightarrow \text{list}(k_3, v_3)$$

While MapReduce revolutionized batch computation, its reliance on writing intermediate state to disk after each Map phase introduces latency for iterative computations.

Zaharia et al. (2012) addressed this limitation by introducing **Resilient Distributed Datasets (RDDs)** and **Apache Spark**. By maintaining intermediate partitions in distributed main memory and tracking transformations through a Directed Acyclic Graph (DAG) lineage, Spark achieves processing speeds up to 100x faster than traditional MapReduce for multi-pass iterative algorithms.

This project implements both paradigms:
- **MapReduce** demonstrates fundamental parallel key-value aggregation across 390+ route and carrier combinations.
- **PySpark** provides high-throughput in-memory DataFrame operations, schema validation, and window aggregations.

---

### 4. Machine Learning for Logistics Delay Forecasting
Prior literature on logistics delay prediction (e.g., Wang et al., 2019; Li et al., 2021) highlights that tree-based ensemble methods—specifically **Random Forest Classifiers** (Breiman, 2001)—consistently outperform linear and kernel models on tabular transportation data due to their ability to model non-linear interactions between route distance, carrier identity, seasonal weather patterns, and vehicle capacities without requiring strict parametric assumptions.

Furthermore, academic rigor demands strict mitigation of **target leakage** (Kaufman et al., 2012). By restricting features exclusively to dispatch-time variables, our architecture ensures empirical integrity.

