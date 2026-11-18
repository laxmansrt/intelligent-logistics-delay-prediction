# Existing vs. Proposed System Analysis

### 1. Existing System Architecture & Constraints

Traditional logistics management systems (LMS) and enterprise resource planning (ERP) suites were designed prior to the emergence of big data distributed architectures.

| Dimension | Existing System | Operational Impact |
|---|---|---|
| **Storage Architecture** | Centralized Relational Database Management Systems (RDBMS - MySQL, PostgreSQL, Oracle). | Fails to scale horizontally when storing time-series GPS telematics and multi-city weather logs. Table locks and disk I/O bottlenecks degrade performance. |
| **Data Ingestion** | Nightly monolithic batch imports via stored procedures. | Stale data; latency between physical events (traffic incident) and database ingestion spans hours or days. |
| **Data Processing** | Single-threaded SQL queries and CPU-bound reporting jobs on one server. | Query timeouts and resource exhaustion when aggregating metrics across millions of historical shipment rows. |
| **Analytics Paradigm** | Descriptive / Historical only ("Where was the shipment yesterday? How many shipments were delayed last quarter?"). | Purely reactive; warehouse managers cannot intervene to avert pending delays before packages depart. |
| **Failure Handling** | Database replication with high overhead; compute failures require restarting entire ETL queries from scratch. | Lengthy maintenance windows and lack of fine-grained partition recovery. |

---

### 2. Proposed Big Data Intelligence Architecture

The proposed system replaces monolithic relational components with a distributed, multi-tiered big data architecture.

```
+-------------------------------------------------------------------------------+
|                             PROPOSED ARCHITECTURE                             |
+-------------------------------------------------------------------------------+
|  DATA SOURCES    | Shipments CSV, Traffic Logs, Weather Stations, GPS Pings   |
+------------------+------------------------------------------------------------+
|  STORAGE LAYER   | Dual-Mode HDFS Abstraction (Tiered raw/, clean/, analytics/)|
|                  | MongoDB NoSQL Document Store with Spatial & Temporal Index |
+------------------+------------------------------------------------------------+
|  PROCESSING      | Hadoop Streaming MapReduce for key-value batch aggregations|
|  ENGINE          | Apache Spark (PySpark) In-Memory DataFrame ETL & Analysis  |
+------------------+------------------------------------------------------------+
|  MACHINE         | Scikit-learn Pipeline (Random Forest vs Logistic Regression)|
|  LEARNING        | Stratified 80/20 Holdout, Zero Target Leakage Validation   |
+------------------+------------------------------------------------------------+
|  APPLICATION     | Flask REST API + HTML5/CSS3/Chart.js Interactive Dashboard  |
+-------------------------------------------------------------------------------+
```

### 3. Comparative Advantage Matrix

| Feature | Existing System | Proposed BDT System |
|---|---|---|
| **Storage Scalability** | Vertical hardware scaling (costly). | Horizontal distributed scaling across commodity nodes via HDFS. |
| **Schema Paradigm** | Rigid Schema-on-Write (DDL migrations). | Flexible Schema-on-Read; handles heterogeneous telemetry. |
| **Computation Model** | Disk-bound SQL joins on single server. | In-memory distributed DAG execution via Apache Spark. |
| **Fault Tolerance** | Manual database recovery snapshots. | Automatic block replication (HDFS) and lineage graph recovery (RDDs). |
| **Predictive Power** | None (Historical summaries only). | Pre-dispatch delay probability, risk categorization, and factor attribution. |
| **Operational Workflow** | Reactive crisis response. | Proactive dispatch adjustments and route rescheduling. |

