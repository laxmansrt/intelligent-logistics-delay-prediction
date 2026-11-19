# Test Cases & Verification Matrix (77/77 Passing)

**Project Title:** Big Data Classification and Prediction for Transportation and Logistics using Apache Hive

---

### 1. Test Suite Summary

The system contains **77 automated pytest test cases** providing end-to-end coverage across configuration, storage abstraction, data validation, Apache Hive integration, HiveQL queries, MapReduce, Spark, Scikit-learn ML, and Flask REST endpoints.

```text
======================= 77 passed in 46.45s ========================
```

---

### 2. Comprehensive Test Matrix

#### Phase 1: Environment & Storage Abstraction Tests (`tests/test_phase1_setup.py` - 22 Tests)
| Test ID | Test Target | Verification Description | Status |
|---|---|---|---|
| TC-SETUP-01 | Directory Scaffolding | Verifies all required project subdirectories exist. | PASS |
| TC-SETUP-02 | Environment Loading | Validates `.env` presence and variable loading. | PASS |
| TC-SETUP-03 | Config Singleton | Checks default port, host, and storage mode settings. | PASS |
| TC-SETUP-04 | Logging Service | Verifies rotating log file generation and format. | PASS |
| TC-SETUP-05..12 | Storage Service (Local) | Tests file save, load, delete, listing, and exists. | PASS |
| TC-SETUP-13..16 | Storage Service (HDFS) | Tests WebHDFS fallback logic and URL generation. | PASS |
| TC-SETUP-17..22 | API Response Helper | Validates standardized JSON envelopes (success/error). | PASS |

#### Phase 2: Data Ingestion & Preprocessing Tests (`tests/test_phase2_ingestion.py` - 26 Tests)
| Test ID | Test Target | Verification Description | Status |
|---|---|---|---|
| TC-INGEST-01..05 | File Validation | Checks file extension, MIME type, and 50MB size limit. | PASS |
| TC-INGEST-06..10 | Path Traversal Security | Prevents malicious filenames (e.g. `../../etc/passwd`). | PASS |
| TC-INGEST-11..15 | Shipment Cleaning | Validates deduplication and missing value imputation. | PASS |
| TC-INGEST-16..20 | Target Variable Label | Verifies `is_delayed = 1` iff actual > scheduled. | PASS |
| TC-INGEST-21..26 | Temporal Parsing | Tests duration calculation and timestamp parsing. | PASS |

#### Phase 3: Distributed Processing & ML Tests (`tests/test_phase3_bigdata_ml.py` - 14 Tests)
| Test ID | Test Target | Verification Description | Status |
|---|---|---|---|
| TC-MR-01 | MapReduce Mapper | Tests key-value emission (`route`, `carrier`, `vehicle`). | PASS |
| TC-MR-02 | MapReduce Reducer | Tests intermediate aggregation across sorted keys. | PASS |
| TC-MR-03 | MapReduce Runner | Tests local pipe execution and output TSV schema. | PASS |
| TC-SPARK-01 | Spark Session | Validates local SparkSession initialization. | PASS |
| TC-SPARK-02 | Spark Cleaning | Tests distributed DataFrame ETL and column types. | PASS |
| TC-SPARK-03 | Spark Route Aggregator | Verifies bottleneck delay rate calculations. | PASS |
| TC-ML-01 | Zero Target Leakage | Confirms actual delivery fields are excluded from X. | PASS |
| TC-ML-02 | Logistic Regression | Benchmarks baseline classifier accuracy and metrics. | PASS |
| TC-ML-03 | Random Forest | Trains primary classifier and validates metrics format. | PASS |
| TC-ML-04 | Delay Inference | Tests single dispatch prediction and risk tiering. | PASS |
| TC-API-01..04 | Flask Endpoints | Tests `/health`, `/shipments`, `/predict`, `/analytics`. | PASS |

#### Phase 4: Apache Hive & HiveQL Analytics Tests (`tests/test_phase4_hive.py` - 15 Tests)
| Test ID | Test Target | Verification Description | Status |
|---|---|---|---|
| TC-HIVE-01 | Hive Service Singleton | Checks Hive service initialization and status dict. | PASS |
| TC-HIVE-02 | Hive Schema Init | Tests DDL script execution (`transportation_logistics_db`). | PASS |
| TC-HIVE-03 | ORC Table Verification | Checks managed `shipments_orc` table and partition schema. | PASS |
| TC-HIVE-04 | Query 01: Total Volume | Executes `01_total_shipments.hql` and checks row count. | PASS |
| TC-HIVE-05 | Query 02: OnTime/Delayed| Executes `02_ontime_vs_delayed.hql` and checks distribution. | PASS |
| TC-HIVE-06 | Query 03: Delay Rate | Executes `03_delay_percentage.hql` and checks mean delay. | PASS |
| TC-HIVE-07 | Query 04: Avg Duration | Executes `04_avg_delivery_duration.hql` by transport mode. | PASS |
| TC-HIVE-08 | Query 05: Top Routes | Executes `05_routes_highest_delays.hql` and checks limit 15. | PASS |
| TC-HIVE-09 | Query 06: Mode Patterns | Executes `06_transportation_mode_analysis.hql`. | PASS |
| TC-HIVE-10 | Query 07: Monthly Trend | Executes `07_monthly_shipment_trends.hql` chronologically. | PASS |
| TC-HIVE-11 | Custom HiveQL Query | Tests arbitrary ad-hoc HiveQL query execution. | PASS |
| TC-HIVE-12 | API: `/api/v1/hive/status` | Tests REST endpoint returning Hive warehouse status. | PASS |
| TC-HIVE-13 | API: `/api/v1/hive/query` | Tests REST endpoint for running canonical queries. | PASS |
| TC-HIVE-14 | API: `/api/v1/hive/scripts`| Tests listing available `.hql` query scripts. | PASS |
| TC-HIVE-15 | View: `/hive-page` | Validates HTML rendering of Apache Hive web console. | PASS |
