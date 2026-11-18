# Module Descriptions

### Module 1: Data Collection & Ingestion (`backend/services/ingestion_service.py`)
- **Purpose:** Ingests multi-source logistics CSV files (shipments, traffic, weather, GPS).
- **Responsibilities:**
  - Enforces file type (`.csv`) and size limits (<= 50 MB) in `backend/utils/validators.py`.
  - Normalizes alternate column names using an alias mapping dictionary.
  - Validates required mandatory columns for each dataset type.
  - Cleans, parses types, and writes raw records to the storage abstraction layer and MongoDB collections.
  - Generates comprehensive ingestion audit reports.

### Module 2: Storage Abstraction Layer (`backend/services/storage_service.py`)
- **Purpose:** Encapsulates distributed storage operations behind a uniform API.
- **Responsibilities:**
  - Supports dual execution modes: `local` (local directory mirror) and `hdfs` (Apache WebHDFS REST API via `hdfs.InsecureClient`).
  - Mirrors standard HDFS tiered hierarchy: `raw/`, `processed/`, `analytics/`, `models/`.
  - Provides uniform file reading, writing, and directory listing methods across both environments.

### Module 3: MapReduce Batch Analytics (`bigdata/mapreduce/`)
- **Purpose:** Executes distributed parallel batch aggregation using Hadoop Streaming principles.
- **Components:**
  - `shipment_mapper.py`: Parses CSV rows and emits key-value pairs formatted with metrics (`route|<orig>-><dest>`, `carrier|<carrier>`, `vehicle|<type>`).
  - `shipment_reducer.py`: Receives sorted inputs from the Shuffle & Sort phase; aggregates total count, delayed count, delay percentage, and average delay duration.
  - `run_mapreduce.py`: Orchestrates execution either natively via `hadoop jar` or locally via UNIX pipes.

### Module 4: Apache Spark / PySpark Processing Engine (`bigdata/spark/`)
- **Purpose:** High-throughput in-memory data transformation, deduplication, and risk aggregation.
- **Components:**
  - `spark_session.py`: Builds a tuned `SparkSession` configured for local or cluster execution.
  - `shipment_processor.py`: Implements distributed ETL: schema casting, deduplication on `shipment_id`, column-mean missing value imputation, and temporal feature extraction.
  - `route_analyzer.py`: Identifies high-risk bottleneck corridors by aggregating delay rates across all origin-destination pairs.
  - `delay_aggregator.py`: Computes multi-dimensional KPIs across carriers, vehicles, and weather conditions.

### Module 5: Machine Learning Delay Prediction (`ml/`)
- **Purpose:** Predicts shipment delay probability and risk category using dispatch-time parameters.
- **Components:**
  - `feature_engineering.py`: Builds a zero-target-leakage feature pipeline using `ColumnTransformer` (StandardScaler for numericals, OneHotEncoder for categoricals).
  - `train_model.py`: Trains and benchmarks a Baseline Logistic Regression against a Primary Random Forest Classifier (100 trees, max depth 12); records accuracy, precision, recall, F1, and confusion matrix.
  - `predict.py`: Real-time inference engine computing delay probabilities, risk tiers (Low/Medium/High), confidence scores, and rule-based contributing factors.

### Module 6: Backend REST API (`backend/routes/`)
- **Purpose:** Exposes clean JSON REST endpoints for all platform capabilities.
- **Blueprints:**
  - `health_bp`: System liveness and diagnostic component probes.
  - `upload_bp`: CSV ingestion, sample data loading, and file listing.
  - `shipments_bp`: Paginated shipment registry queries, multi-attribute filtering, and KPI stats.
  - `predict_bp`: Single and batch ML inference, prediction logging, and model retraining triggers.
  - `analytics_bp`: Feeds structured analytical distributions to frontend charts.
  - `jobs_bp`: Asynchronous distributed job execution and audit trails.

### Module 7: Interactive Dashboard Frontend (`frontend/`)
- **Purpose:** Operator-facing logistics intelligence dashboard.
- **Components:**
  - `base.html`: Professional sidebar navigation, responsive container, and topbar system health status pills.
  - `index.html`: Real-time KPI summary cards, Chart.js delay contributor doughnuts, carrier comparison bars, and recent dispatch tables.
  - `shipments.html`: Live searchable, filterable shipment tracking table with server-side pagination.
  - `predict.html`: Interactive dispatch simulator with dynamic risk categorization and contributing factor attribution.
  - `analytics.html`: Deep-dive route risk tables and correlation vs. causation guidance.
  - `processing.html`: Big Data control panel with real-time log terminal and job history table.
  - `model.html`: Model evaluation benchmarks, confusion matrix visualization, and feature importance bar charts.
  - `upload.html`: Multi-source dataset upload panel with bundled sample data loader.

