# Implementation Steps & Execution Guide

**Project Title:** Big Data Classification and Prediction for Transportation and Logistics using Apache Hive

Follow these step-by-step instructions to reproduce the complete project environment on a developer workstation.

---

### Step 1: Environment Setup & Dependency Installation
1. Navigate to the repository root directory:
   ```bash
   cd intelligent-logistics-delay-prediction
   ```
2. Copy environment template to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Install required Python packages:
   ```bash
   pip3 install -r requirements.txt --break-system-packages
   ```
   *(Dependencies include PySpark, PyHive, thrift, scikit-learn, pandas, numpy, flask, and joblib).*

---

### Step 2: Multi-Source Data Generation (Clearly Labeled Synthetic)
Generate reproducible transportation and telematics records for evaluation:
```bash
python3 scripts/generate_sample_data.py
```
*Generated files land in `data/sample/`:*
- `sample_shipments.csv` (14,000+ logistics rows across Ground, Air, Rail, Sea)
- `sample_traffic.csv` (~3,000 route congestion logs)
- `sample_weather.csv` (~1,500 meteorological observations)
- `sample_gps.csv` (~8,000 vehicle GPS breadcrumbs)

---

### Step 3: Apache Hive Integration & HiveQL Analytics (Central Module)
Initialize the Hive database, staging table, managed ORC partitioned table, and execute all 7 canonical HiveQL queries:
```bash
python3 scripts/run_hive_queries.py
```
*Expected Terminal Output:*
- Database `transportation_logistics_db` created.
- Table `shipments_raw` loaded with CSV records.
- Partitioned ORC table `shipments_orc` generated with Snappy compression across `Air`, `Ground`, `Rail`, `Sea`.
- All 7 HiveQL queries executed:
  1. `01_total_shipments.hql`
  2. `02_ontime_vs_delayed.hql`
  3. `03_delay_percentage.hql`
  4. `04_avg_delivery_duration.hql`
  5. `05_routes_highest_delays.hql`
  6. `06_transportation_mode_analysis.hql`
  7. `07_monthly_shipment_trends.hql`
- Results saved to `data/analytics/hive/` as structured JSON reports.

*Optional Docker Cluster Execution:*
```bash
docker compose -f docker-compose.hive.yml up -d
```

---

### Step 4: Machine Learning Model Training
Train and benchmark Logistic Regression against Random Forest Classifier (with strict zero target leakage):
```bash
python3 scripts/train_model.py
```
*Model artifacts generated in `data/models/`:*
- `random_forest_model.joblib`: Serialized Scikit-learn Pipeline
- `logistic_regression_model.joblib`: Serialized Baseline Pipeline
- `evaluation_metrics.json`: Empirical benchmark metrics (Accuracy: 85.8%, AUC: 0.918)

---

### Step 5: Distributed Batch Processing (MapReduce & Spark)
Execute auxiliary distributed processing jobs:
```bash
# Run Hadoop Streaming MapReduce batch aggregation:
python3 bigdata/mapreduce/run_mapreduce.py

# Run PySpark distributed ETL, route analysis, and delay rollups:
python3 scripts/run_spark_job.py
```

---

### Step 6: Launch Web Dashboard
Start the Flask application on port **5050**:
```bash
python3 run.py
```
Open your browser and navigate to:  
👉 **`http://localhost:5050`**

Explore:
- `/` - Overview & KPIs Banner
- `/hive-page` - Apache Hive Analytics & HiveQL Console
- `/shipments-page` - Filterable Shipment Registry
- `/predict-page` - Interactive Delay Prediction Simulator
- `/analytics-page` - Transportation & Route Patterns
- `/model-page` - Model Benchmarks & Confusion Matrix
- `/processing-page` - Big Data Processing Job Controls
- `/upload-page` - Dataset Upload Panel

---

### Step 7: Run Automated Verification Tests
Verify all 77 automated unit and integration tests:
```bash
python3 -m pytest tests/ -v
```
All 77 test cases will pass in ~45 seconds.
