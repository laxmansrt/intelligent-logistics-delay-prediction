# Use Case Diagram & Actor Specifications

**Project Title:** Big Data Classification and Prediction for Transportation and Logistics using Apache Hive

---

### 1. Primary Actors
1. **Logistics Dispatch Manager / Operator:** Responsible for scheduling shipments, monitoring transit bottlenecks, simulating delay risks, and initiating route diversions.
2. **Big Data Engineer / Analyst:** Manages the Apache Hive data warehouse, oversees HiveQL query execution, inspects table partitions, and monitors batch jobs.
3. **Machine Learning Engineer:** Retrains models, benchmarks classification metrics, inspects feature importance, and ensures zero target leakage.
4. **Automated Data Feed / System Daemon:** Periodic background ingestion of multi-source CSV files, GPS telematics, and weather updates.

---

### 2. Textual Use Case Diagram

```
                                  +=============================================+
                                  |    TRANSPORTATION & LOGISTICS SYSTEM        |
                                  +=============================================+
                                  |                                             |
   ( Logistics Dispatch ) ───────>|  [UC-01: View Overview Analytics & KPIs]   |
   (      Manager       )         |                                             |
                                  |  [UC-02: Search & Filter Shipment Registry] |
                                  |                                             |
                                  |  [UC-03: Simulate Delay Risk & Predict]     |
                                  |                                             |
   ( Big Data Engineer  ) ───────>|  [UC-04: Initialize Apache Hive Warehouse] |
   (   & Data Analyst   )         |                                             |
                                  |  [UC-05: Execute Canonical HiveQL Queries]  |
                                  |                                             |
                                  |  [UC-06: Execute Custom HiveQL Script]      |
                                  |                                             |
                                  |  [UC-07: Trigger PySpark / MapReduce Jobs]  |
                                  |                                             |
   ( ML Engineer / Ops  ) ───────>|  [UC-08: Benchmark & Retrain ML Models]     |
                                  |                                             |
                                  |  [UC-09: Inspect Feature Importances & ROC] |
                                  |                                             |
   ( Automated Data Feed) ───────>|  [UC-10: Upload & Ingest Multi-Source CSV]  |
                                  |                                             |
                                  +=============================================+
```

---

### 3. Detailed Use Case Descriptions

#### UC-05: Execute Canonical HiveQL Queries
- **Primary Actor:** Big Data Engineer / Data Analyst.
- **Preconditions:** Apache Hive warehouse initialized; `shipments_orc` table populated with partitioned logistics records.
- **Main Flow:**
  1. Actor navigates to the `/hive-page` on the web dashboard.
  2. Actor selects any of the 7 pre-built HiveQL query cards (e.g., *On-Time vs Delayed Classification*, *Top 15 Bottlenecks*, *Monthly Trends*).
  3. System dispatches request to `/api/v1/hive/query/<query_name>`.
  4. Backend Hive service compiles and executes HiveQL over partitioned ORC tables.
  5. System returns execution time in milliseconds and tabular records rendered dynamically in the UI.
- **Postconditions:** Query output displayed and cached in analytical results store.

#### UC-03: Simulate Delay Risk & Predict
- **Primary Actor:** Logistics Dispatch Manager.
- **Preconditions:** Random Forest classification model trained and serialized in `data/models/`.
- **Main Flow:**
  1. Actor navigates to `/predict-page`.
  2. Actor inputs pre-dispatch parameters: Origin City, Destination City, Carrier, Vehicle Type, Distance (km), Weight (kg), Category, Scheduled Hour, and Day of Week.
  3. System verifies that no post-dispatch target leakage fields are included.
  4. Machine learning pipeline encodes features and produces binary classification (`On-Time` vs `Delayed`), delay probability percentage, and risk tier (`Low`, `Medium`, `High`).
  5. System highlights the top operational factors driving the risk calculation.
- **Postconditions:** Prediction result displayed to operator for proactive routing decisions.
