# Data Flow Diagrams (DFD)

**Project Title:** Big Data Classification and Prediction for Transportation and Logistics using Apache Hive

---

### 1. DFD Level 0 (Context Diagram)

The Level 0 Context Diagram depicts the entire platform as a single operational boundary interacting with external entities (Logistics Operator, Data Sources, and External Distributed Clusters).

```
                      +-----------------------------+
                      |   Multi-Source Data Feeds   |
                      | (Shipments, Traffic, Weather)|
                      +-----------------------------+
                                     │
                                     │ Raw Logistics Records (CSV)
                                     ▼
+---------------------+   HTTP/REST   +---------------------------------------------+
|                     | <───────────> |                                             |
|  Logistics Operator |               |   Big Data Classification and Prediction    |
|  (User / Analyst)   |   Queries &   |  for Transportation and Logistics using    |
|                     |   Parameters  |                 Apache Hive                 |
+---------------------+ <───────────> |                                             |
                                      +---------------------------------------------+
                                                     │              ▲
                                      HDFS / HiveQL  │              │ Metastore
                                      I/O Requests   ▼              │ & Data Splits
                                      +---------------------------------------------+
                                      |     Hadoop HDFS & Apache Hive Warehouse     |
                                      +---------------------------------------------+
```

---

### 2. DFD Level 1 (High-Level Process Decomposition)

```
[External Sources]
       │
       │ (1) Ingestion
       ▼
( Process 1.0 ) ─────── ( Raw Data Lake )
Data Validation &       data/raw/
Cleaning Pipeline
       │
       │ (2) Clean Records
       ▼
( Process 2.0 ) ─────── ( Apache Hive Warehouse )
Hive Staging & DDL      transportation_logistics_db
shipments_raw Table     shipments_orc (Partitioned by mode)
       │
       ├─────────────────────────────────┐
       │ (3) HiveQL Query Execution       │ (4) Feature Selection (Pre-Dispatch Only)
       ▼                                 ▼
( Process 3.0 )                   ( Process 4.0 )
HiveQL Big Data Analytics         ML Classification Pipeline
7 Core Analytical Queries         Random Forest Classifier
       │                                 │
       │ Aggregated Metrics Tables       │ Classifications & Delay Probabilities
       ▼                                 ▼
( Process 5.0 ) <────────────────────────┘
Flask REST API & Blue-White Dashboard
       │
       ▼
[Logistics Operator / UI View]
```

---

### 3. DFD Level 2 (Process 3.0 - Apache Hive Integration Deep Dive)

```
               +─────────────────────────────────────────+
               | shipments_raw (External CSV Staging)    |
               +─────────────────────────────────────────+
                                    │
                                    │ INSERT OVERWRITE TABLE shipments_orc
                                    │ PARTITION (transportation_mode)
                                    ▼
               +─────────────────────────────────────────+
               | shipments_orc (Managed Columnar ORC)    |
               | - Snappy Compression                    |
               | - Partitions: Air, Ground, Rail, Sea    |
               +─────────────────────────────────────────+
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
         ▼                          ▼                          ▼
   [Query 01 & 02]            [Query 03 & 04]            [Query 05 & 06]
Volume & On-Time vs       Delay % & Average Transit   Top 15 Bottlenecks & Mode
Delayed Classification    Duration Calculations       Efficiency Patterns
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
                                    ▼
               +─────────────────────────────────────────+
               | Hive Analytics Results (JSON / Metrics) |
               +─────────────────────────────────────────+
                                    │
                                    ▼
               +─────────────────────────────────────────+
               | Flask Hive Service & Analytics Web UI   |
               +─────────────────────────────────────────+
```
