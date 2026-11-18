# Data Flow Diagrams (DFD)

### 1. DFD Level 0 (Context Diagram)

```
                       +---------------------------------------+
                       |                                       |
                       |              Logistics                |
                       |              Dispatcher               |
                       |                                       |
                       +-------------------+-------------------+
                                           |
                   Dispatch Parameters /   |   Real-time Risk Category /
                   CSV Uploads             |   Delay Probability & Factors
                                           |
                                           v
                       +---------------------------------------+
                       |                                       |
                       |                 0.0                   |
                       |         Intelligent Logistics         |
                       |       Delay Prediction Platform       |
                       |               (System)                |
                       |                                       |
                       +-------------------+-------------------+
                                           |
                           Raw Telematics  |   Clean Data Lake /
                           Storage & Index |   Analytical Aggregations
                                           |
                                           v
                       +---------------------------------------+
                       |                                       |
                       |              Data Stores              |
                       |        (HDFS & MongoDB DB)            |
                       |                                       |
                       +---------------------------------------+
```

---

### 2. DFD Level 1 (High-Level Process Decomposition)

```
[CSV Datasets] ──> (1.0 Ingestion & Validation) ──> [data/raw/ / HDFS]
                             │
                             ▼
                   (2.0 MongoDB Bulk Persist) ──> [MongoDB Database]
                             │
                             ▼
                   (3.0 PySpark ETL & Cleaning) ──> [data/processed/]
                             │
                             ├──> (4.0 MapReduce Batch Analytics) ──> [Analytics TSV]
                             │
                             ▼
                   (5.0 ML Model Training & Eval) ──> [data/models/ Pipeline]
                             │
                             ▼
[User Request] ──> (6.0 Real-time Inference Engine) ──> [Predicted Risk to UI]
```

---

### 3. DFD Level 2 (Machine Learning Inference Flow)

```
[Dispatch Form Input]
  │
  ▼
(Validate Feature Schema)
  │
  ├─── Origin / Destination City
  ├─── Transport Vehicle & Carrier
  ├─── Distance (km) & Weight (kg)
  └─── Scheduled Departure Hour
  │
  ▼
(Feature Transformer Pipeline)
  │
  ├─── StandardScaler (Distance, Weight, Hour, Day, Month)
  └─── OneHotEncoder (Vehicle, Carrier, Category, Cities)
  │
  ▼
(RandomForestClassifier.predict_proba)
  │
  ├─── Probability < 0.35  ──> [Low Risk Badge (Green)]
  ├─── 0.35 <= P < 0.65    ──> [Medium Risk Badge (Amber)]
  └─── Probability >= 0.65 ──> [High Risk Badge (Red)]
  │
  ▼
(Contributing Factor Attribution Logic)
  │
  ▼
(JSON Response to Frontend UI & MongoDB Persistence)
```

