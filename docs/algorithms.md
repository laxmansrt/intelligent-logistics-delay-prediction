# Algorithms & Big Data Computation Mechanics

### 1. MapReduce Streaming Aggregation Algorithm

The Hadoop Streaming MapReduce pipeline processes millions of raw shipment lines via standard I/O streams:

#### Algorithm 1: ShipmentMapper (`bigdata/mapreduce/shipment_mapper.py`)
```text
Input:  Stream of CSV lines from STDIN
Output: Tab-delimited (Key, Value) pairs on STDOUT

1. Detect header row; identify indices for:
   origin_city, destination_city, carrier, vehicle_type, is_delayed, delay_minutes.
2. For each subsequent line in STDIN:
   a. Parse comma-separated fields.
   b. RouteKey ← Concatenate(origin_city, "->", destination_city)
   c. IsDelayed ← 1 if is_delayed in ("1", "true") else 0
   d. DelayMinutes ← float(delay_minutes)
   e. Emit ("route|" + RouteKey, "1\t" + IsDelayed + "\t" + DelayMinutes)
   f. Emit ("carrier|" + carrier, "1\t" + IsDelayed + "\t" + DelayMinutes)
   g. Emit ("vehicle|" + vehicle_type, "1\t" + IsDelayed + "\t" + DelayMinutes)
   h. Emit ("overall|ALL", "1\t" + IsDelayed + "\t" + DelayMinutes)
```

#### Algorithm 2: ShipmentReducer (`bigdata/mapreduce/shipment_reducer.py`)
```text
Input:  Sorted stream of (Key, Value) pairs from Shuffle & Sort phase on STDIN
Output: Aggregated metrics TSV on STDOUT

1. Initialize current_key ← null, total_count ← 0, delayed_count ← 0, total_delay_mins ← 0.0
2. For each line in STDIN:
   a. Split line into (key, count, delayed, delay_minutes)
   b. If current_key != null and current_key != key:
        delay_rate ← (delayed_count / total_count) * 100.0
        avg_delay  ← (total_delay_mins / delayed_count) if delayed_count > 0 else 0.0
        Emit (Category, Dimension, total_count, delayed_count, delay_rate, avg_delay)
        Reset accumulators to 0
   c. current_key ← key
   d. total_count += count
   e. delayed_count += delayed
   f. total_delay_mins += delay_minutes
3. Emit final aggregated record for last current_key.
```

---

### 2. PySpark In-Memory DataFrame Processing Algorithm

The PySpark ETL pipeline (`bigdata/spark/shipment_processor.py`) optimizes memory and CPU core utilization:

```text
1. Initialize SparkSession with driver memory 2GB and local[*] master.
2. Spark DataFrame Read:
   raw_df ← spark.read.option("header", "true").option("inferSchema", "true").csv(path)
3. Deduplication:
   dedup_df ← raw_df.dropDuplicates(["shipment_id"])
4. Type Enforcement & Casting:
   Cast distance_km, weight_kg to DoubleType; is_delayed to IntegerType.
   Convert string timestamps to TimestampType via F.to_timestamp().
5. Missing Value Imputation:
   Compute Column Means for distance_km and weight_kg using F.avg().
   Impute null values via clean_df.na.fill().
6. Feature Extraction:
   Derive scheduled_hour ← F.hour(scheduled_pickup)
   Derive scheduled_day_of_week ← F.dayofweek(scheduled_pickup)
   Derive scheduled_month ← F.month(scheduled_pickup)
   Derive planned_transit_hours ← (unix_timestamp(delivery) - unix_timestamp(pickup)) / 3600
7. Distributed Partition Persistence:
   Save to data/processed/shipments_clean/clean_shipments.csv
```

---

### 3. Machine Learning: Random Forest Classification Algorithm

#### Algorithm 3: Delay Prediction Model Training (`ml/train_model.py`)
```text
Input: Clean historical shipments dataset
Output: Serialized Pipeline (.joblib) & Evaluation Report JSON

1. Preprocessing (No Target Leakage):
   Features X ← {distance_km, weight_kg, scheduled_hour, scheduled_day_of_week, scheduled_month,
                 vehicle_type, carrier, category, origin_city, destination_city}
   Target y ← {is_delayed} (0 or 1)
   EXCLUDE: actual_pickup, actual_delivery, delay_minutes, delay_reason, status.
2. Stratified Train/Test Split:
   (X_train, X_test, y_train, y_test) ← train_test_split(X, y, test_size=0.20, stratify=y, random_state=42)
3. Construct Feature Pipeline:
   ColumnTransformer:
     - Numeric: StandardScaler()
     - Categorical: OneHotEncoder(handle_unknown='ignore')
4. Model 1 (Baseline):
   Fit LogisticRegression(max_iter=500) on X_train.
   Compute Baseline Accuracy, Precision, Recall, F1 on X_test.
5. Model 2 (Primary Classifier):
   Fit RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42) on X_train.
   Compute Primary Accuracy, Precision, Recall, F1, Confusion Matrix on X_test.
6. Extract Gini Feature Importances from Random Forest ensemble.
7. Save serialized model to data/models/delay_predictor.joblib.
```

