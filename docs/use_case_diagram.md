# Use Case Specifications

### 1. Primary Actors
1. **Logistics Dispatcher / Operations Manager:** Creates shipments, queries status, evaluates transit vulnerability prior to vehicle dispatch, and requests alternative routing.
2. **Big Data Engineer:** Monitors PySpark distributed ETL, executes MapReduce batch jobs, and configures storage clusters (HDFS/local).
3. **Data Scientist / ML Engineer:** Evaluates model benchmarks (Random Forest vs Baseline Logistic Regression), inspects confusion matrices, and triggers model retraining.

---

### 2. Use Case Matrix

| Use Case ID | Use Case Name | Actor | Description | Preconditions |
|---|---|---|---|---|
| **UC-01** | Ingest Multi-Source Datasets | Operations Manager | Uploads CSV datasets (Shipments, Traffic, Weather, GPS) via web interface. | User has valid CSV file <= 50MB. |
| **UC-02** | Query Shipment Registry | Operations Manager | Searches, filters, and paginates through active and historical shipments. | Ingested data exists. |
| **UC-03** | Predict Shipment Delay Risk | Operations Manager | Inputs proposed route parameters to receive delay probability, risk tier, and factors. | Model pipeline is trained. |
| **UC-04** | Run PySpark ETL Pipeline | Big Data Engineer | Triggers distributed Spark DataFrame cleaning, deduplication, and schema enforcement. | Raw data is present. |
| **UC-05** | Execute MapReduce Batch Job | Big Data Engineer | Submits streaming MapReduce job to compute route and carrier delay rates. | Input dataset is available. |
| **UC-06** | Analyze Route Bottlenecks | Operations Manager | Visualizes delay percentages across major interstate corridors. | Analytics have run. |
| **UC-07** | Inspect Model Evaluation | ML Engineer | Reviews accuracy, precision, recall, F1-score, and confusion matrix. | Model metrics generated. |
| **UC-08** | Retrain Predictive Pipeline | ML Engineer | Re-fits Random Forest pipeline on newly ingested shipment data. | Updated dataset available. |

