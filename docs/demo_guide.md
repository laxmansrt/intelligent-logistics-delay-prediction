# University College Review & Viva Voce Demonstration Guide

**Project Title:** Intelligent Logistics Delay Prediction Using Big Data Analytics  
**Course:** Big Data Technologies (BDT)  

---

## 🎯 5-Minute Live Demonstration Script for Evaluators

### Step 1: Open the Application
1. Ensure the server is running on:
   👉 **`http://localhost:5050`**
2. Point out the top header badges:
   - `Storage: LOCAL` (Mirrors HDFS block architecture)
   - `Spark: local[*]` (PySpark utilizing all host CPU cores)

### Step 2: Overview Dashboard (`/`)
1. Show the **Real-Time KPI Cards**:
   - Total Shipments (2,000+)
   - On-Time vs Delayed Count
   - System Delay Percentage (~33%)
   - Average Delay Minutes (~180 mins)
   *(Explain to the evaluator: "All stats are computed dynamically from real datasets; no hardcoded values!")*
2. Highlight the interactive **Chart.js** widgets:
   - **Delay Contributors Breakdown** (Traffic Congestion, Weather, Road Closures)
   - **Carrier Comparative Delay Performance** (BlueDart vs Delhivery vs FedEx)
3. Show the **Recent Dispatches Table** with status badges.

### Step 3: Interactive Delay Prediction Simulator (`/predict-page`)
1. Demonstrate a live prediction:
   - Origin: `Mumbai`, Destination: `Delhi`
   - Distance: `1420 km`, Vehicle: `Heavy Truck`
   - Carrier: `BlueDart`, Departure Hour: `8 AM` (Peak rush hour)
2. Click **⚡ Predict Delay Risk**:
   - Show the dynamic result: **Medium / High Risk**
   - Delay Probability percentage bar & Confidence score
   - Contextual **Contributing Factors**:
     - *"Long-haul route distance (1420 km) increases transit vulnerability"*
     - *"Departure scheduled during peak traffic hours (08:00)"*
   *(Explain: "Zero target leakage — predictions use only pre-dispatch parameters!")*

### Step 4: Big Data Processing Console (`/processing-page`)
1. Click **Run MapReduce Job**:
   - Watch the terminal console display the execution of `shipment_mapper.py` & `shipment_reducer.py`.
   - Point out that it aggregates over 390 dimension combinations in ~0.03 seconds!
2. Click **Run PySpark ETL Job**:
   - Shows distributed DataFrame deduplication, schema casting, and missing value imputation.
3. Review the **Processing Jobs Audit History** table.

### Step 5: Model Evaluation & Benchmark (`/model-page`)
1. Review the comparative table:
   - **Baseline (Logistic Regression):** ~64.25% Accuracy
   - **Primary Model (Random Forest Classifier):** ~66.00% Accuracy
2. Review the **2x2 Confusion Matrix** (True Positives, False Positives, True Negatives, False Negatives).
3. Review the **Feature Importance Chart** (Cargo weight, distance, and departure hour top the rankings).

### Step 6: Automated Test Verification
Run in terminal to demonstrate software engineering quality:
```bash
python3 -m pytest tests/ -v
```
*(All 62 tests pass in ~30s!)*

---

## ❓ Common Viva Voce Questions & Model Answers

**Q1: How does your project demonstrate Big Data rather than standard web development?**  
> *"Our project demonstrates 4 foundational BDT pillars: (1) Storage abstraction mirroring HDFS NameNode and DataNode directory structures; (2) Custom Hadoop Streaming MapReduce algorithms executing independent mapping and shuffle-and-sort reducing; (3) Apache Spark in-memory DataFrame ETL and route aggregations; and (4) Schema-on-Read processing over multi-source semi-structured telematics."*

**Q2: What is Target Leakage and how did you prevent it?**  
> *"Target leakage occurs when training data includes variables only known after an event has already occurred. In delay prediction, naive models mistakenly include `actual_delivery_time`, `transit_duration`, or `delay_reason`. Our feature engineering pipeline strictly excludes these, training only on variables known at order dispatch time."*

**Q3: Why use MongoDB alongside HDFS?**  
> *"HDFS is an append-only distributed file system designed for high-throughput batch sequential scans (MapReduce and Spark). MongoDB is an indexed document store providing sub-millisecond point lookups, geospatial indexing, and real-time dashboard queries for logistics operators."*

**Q4: Can this project run on a real Hadoop cluster?**  
> *"Yes. By setting `STORAGE_MODE=hdfs` and `SPARK_MODE=cluster` in `.env`, the storage service seamlessly switches from the local filesystem mirror to Apache WebHDFS, and PySpark connects to a standalone Spark Master or YARN cluster without changing any application code."*

