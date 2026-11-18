# Implementation Steps & Execution Guide

### Phase 1: Environment Initialization & Directory Scaffolding
1. Clone the project repository and set up a clean Python 3.10+ virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt --break-system-packages
   ```
3. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```

---

### Phase 2: Multi-Source Sample Data Generation
Generate synthetic sample datasets for shipments, traffic congestion, weather observations, and GPS telematics:
```bash
python3 scripts/generate_sample_data.py
```
*Generated files land in `data/sample/`:*
- `sample_shipments.csv` (~2,000 rows, 33% delay rate)
- `sample_traffic.csv` (~3,000 rows, congestion levels 1-5)
- `sample_weather.csv` (~1,500 rows, precipitation, temperature, conditions)
- `sample_gps.csv` (~8,000 waypoints, coordinates, speed, heading)

---

### Phase 3: Database & Index Initialization (Optional if MongoDB is running)
```bash
brew services start mongodb-community  # macOS
python3 scripts/init_db.py
```
*Creates all 7 collections and compound indexes for route, status, and timestamp queries.*

---

### Phase 4: Big Data Processing (MapReduce & PySpark)
1. Execute MapReduce Batch Analytics:
   ```bash
   python3 bigdata/mapreduce/run_mapreduce.py
   ```
   *Aggregates 390+ dimension combinations in ~0.03 seconds.*

2. Execute PySpark ETL, Route Analysis, and Delay Aggregations:
   ```bash
   python3 scripts/run_spark_job.py --job all
   ```
   *Saves clean datasets to `data/processed/` and analytical rollups to `data/analytics/`.*

---

### Phase 5: Machine Learning Model Training & Evaluation
Train Baseline Logistic Regression and Primary Random Forest Classifier:
```bash
python3 scripts/train_model.py
```
*Outputs evaluation metrics JSON and saves the trained pipeline to `data/models/delay_predictor.joblib`.*

---

### Phase 6: Automated Testing
Verify system functionality across 62 automated tests:
```bash
python3 -m pytest tests/ -v
```

---

### Phase 7: Web Application Launch
Launch the web intelligence dashboard:
```bash
python3 run.py
```
Navigate to:
👉 **`http://localhost:5050`**

