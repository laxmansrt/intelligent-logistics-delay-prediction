# Algorithms & Big Data Computation Mechanics

**Project Title:** Big Data Classification and Prediction for Transportation and Logistics using Apache Hive

---

### 1. Apache Hive & HiveQL Distributed Query Execution Mechanics

Apache Hive serves as the **central Big Data technology** for data warehousing and analytics. When a declarative HiveQL query is executed, the Hive system processes it through a multi-stage compilation and execution pipeline:

```
HiveQL Query String
        ↓
  [1. Parser]          --> Validates SQL syntax and builds Abstract Syntax Tree (AST)
        ↓
  [2. Semantic Analyzer] --> Resolves table/column names against Hive Metastore
        ↓
  [3. Logical Plan & Optimizer] --> Applies Predicate Pushdown & Column Pruning
        ↓
  [4. Physical Plan Generator]  --> Compiles into Directed Acyclic Graph (DAG)
        ↓
  [5. Vectorized ORC Execution] --> Executes across data splits reading compressed stripes
        ↓
Aggregated Result Records
```

#### Key Hive Optimizations Demonstrated:
1. **Dynamic Partition Pruning:** Queries with `WHERE transportation_mode = 'Air'` immediately filter out unrelated partition directories on disk, saving up to 75% I/O overhead.
2. **ORC Vectorized Reader:** Operates on arrays of 1,024 values per CPU cycle instead of row-by-row iteration, reducing function call overhead and maximizing cache locality.
3. **Stripe-Level Statistics:** ORC stripes contain min/max indexes per column. If a query filters for `distance_km > 1000`, stripes where `max(distance_km) < 1000` are completely skipped without decompression.

---

### 2. MapReduce Streaming Aggregation Algorithm

The Hadoop Streaming MapReduce pipeline processes millions of raw shipment lines via standard I/O streams:

#### Algorithm 1: ShipmentMapper (`bigdata/mapreduce/shipment_mapper.py`)
```text
Input:  Stream of CSV lines from STDIN
Output: Tab-delimited (Key, Value) pairs on STDOUT

1. Detect header row; identify column indices for:
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

### 3. PySpark In-Memory DataFrame Processing Algorithm

The PySpark ETL pipeline (`bigdata/spark/shipment_processor.py`) utilizes in-memory Catalyst optimizations:

```text
Algorithm 3: Distributed DataFrame ETL
1. Load raw CSV into Spark DataFrame with schema inference.
2. Deduplicate records based on unique shipment_id.
3. Impute missing numeric values using column medians.
4. Compute derived temporal columns:
   - scheduled_hour ← hour(to_timestamp(scheduled_pickup))
   - scheduled_day_of_week ← dayofweek(to_timestamp(scheduled_pickup))
   - scheduled_month ← month(to_timestamp(scheduled_pickup))
5. Partition dataset by transportation_mode and persist to data/processed/.
```

---

### 4. Machine Learning Classification & Methodology

To classify shipments into On-Time vs Delayed before dispatch, we employ supervised classification with strict **zero target leakage**.

#### 4.1 Feature Selection (Pre-Dispatch Only)
| Feature Name | Type | Description |
|---|---|---|
| `origin_city` | Categorical (One-Hot) | Departure metropolis |
| `destination_city`| Categorical (One-Hot) | Arrival metropolis |
| `carrier` | Categorical (One-Hot) | Operating logistics company |
| `vehicle_type` | Categorical (One-Hot) | Transportation vehicle category |
| `category` | Categorical (One-Hot) | Cargo commodity type |
| `distance_km` | Numeric (Scaled) | Total transit road/air distance |
| `weight_kg` | Numeric (Scaled) | Cargo mass |
| `scheduled_hour` | Numeric (Cyclical) | Hour of scheduled departure (0-23) |
| `scheduled_day_of_week` | Numeric (Cyclical) | Day of week (1-7) |
| `scheduled_month`| Numeric (Cyclical) | Calendar month (1-12) |

*Excluded Target Leakage Variables:* `actual_delivery`, `actual_pickup`, `delay_minutes`, `delay_reason`, `delivery_duration_hours`.

#### 4.2 Primary Candidate: Random Forest Classifier
Ensemble of $B = 100$ decorrelated decision trees. For each tree $b$:
1. Draw a bootstrap sample $Z^*$ of size $N$ from training data.
2. Grow an unpruned tree $T_b$ by recursively partitioning nodes:
   - Select $m = \sqrt{p}$ features at random from $p$ total features.
   - Pick the best feature/split-point using Gini Impurity:
     $$G = 1 - \sum_{k=1}^{C} p_k^2$$
3. Aggregate predictions across all trees via majority voting / probability averaging:
   $$\hat{P}(Y=1|x) = \frac{1}{B} \sum_{b=1}^{B} T_b(x)$$

#### 4.3 Baseline Candidate: Logistic Regression
Models the log-odds of a shipment delay as a linear combination of input features:
$$\log\left(\frac{P(Y=1|x)}{1 - P(Y=1|x)}\right) = \beta_0 + \sum_{j=1}^{p} \beta_j x_j$$
Trained using L-BFGS optimizer with $L_2$ regularization.
