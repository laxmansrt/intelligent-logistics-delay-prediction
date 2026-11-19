# System Requirements Specification

**Project Title:** Big Data Classification and Prediction for Transportation and Logistics using Apache Hive

---

### 1. Hardware Requirements

The platform is engineered to operate efficiently on standard student development workstations without necessitating expensive cloud infrastructure:

| Component | Minimum Specification | Recommended Specification (Target Dev Machine) |
|---|---|---|
| **Processor** | Dual-Core 64-bit x86 or ARM CPU (2.0 GHz+) | **Apple M-Series (Apple Silicon M1/M2/M3/M4) or Intel/AMD 8-Core CPU** |
| **Random Access Memory (RAM)**| 8 GB Unified / System RAM | **16 GB Unified Memory (Development Machine: MacBook Air M4)** |
| **Disk Storage** | 10 GB free solid-state storage (SSD) | **25 GB SSD Free Storage** |
| **Operating System** | macOS 12+, Ubuntu 20.04+ LTS, or Windows 11 (WSL2) | **macOS Sonoma / Sequoia (Darwin ARM64)** |
| **Display Resolution** | 1366 x 768 pixels | **1920 x 1080 (FHD) or Retina Display** |

---

### 2. Software Requirements

#### 2.1 Core Runtime & Programming Languages
- **Python:** 3.10 to 3.14 (Verified on Python 3.14.3)
- **Java Virtual Machine (JVM):** OpenJDK 11, 17, or 21 (Verified on Java 26 / OpenJDK on macOS)
- **Shell / Terminal:** Zsh or Bash

#### 2.2 Big Data & Warehousing Technologies
- **Apache Hive:** Hive 4.0.0 / Embedded Hive Metastore & Catalog via `enableHiveSupport()`
- **Query Language:** Declarative **HiveQL** (DDL, DML, and Analytical Queries)
- **File & Serialization Formats:** Optimized Row Columnar (**ORC**) with Snappy compression, CSV (OpenCSV SerDe)
- **Apache Spark / PySpark:** PySpark 3.5+ / 4.0+ with local master (`local[*]`)
- **Apache Hadoop:** Hadoop Streaming 3.x (MapReduce compatible streaming runner)
- **Docker & Docker Compose:** Docker Engine 24+ / Docker Desktop (ARM64 Apple Silicon compatible)

#### 2.3 Machine Learning & Data Science Libraries
- **Scikit-learn:** 1.3+ to 1.9+ (Random Forest Classifier, Logistic Regression, Pipeline, ColumnTransformer, Metrics)
- **Pandas:** 2.0+ (DataFrame manipulation and schema normalization)
- **NumPy:** 1.24+ (Vectorized mathematical operations)
- **Joblib:** 1.3+ (Model persistence and serialization)

#### 2.4 Web Backend & Frontend
- **Backend Framework:** Flask 3.0+ (Application factory, modular Blueprints)
- **Cross-Origin Resource Sharing:** Flask-CORS 4.0+
- **Frontend Stack:** HTML5, CSS3 (Modern Blue & White logistics theme), Vanilla JavaScript ES6+
- **Data Visualization:** Chart.js 4.4+ (Doughnut, Bar, Line charts loaded via CDN)
- **Database (NoSQL):** MongoDB Community Edition 6.0+ (or local JSON fallback mode)

---

### 3. Apple Silicon (M4, 16GB) Configuration & Tuning
To guarantee smooth execution on macOS Apple Silicon:
- **PySpark Memory Allocation:** Spark driver memory set to `2g` (`spark.driver.memory=2g`) to avoid memory pressure.
- **Random Forest Concurrency:** `n_jobs=1` to prevent fork lock contention under Python multiprocessing on macOS.
- **Port Assignment:** Default web server port configured to **5050** (`FLASK_PORT=5050`) to avoid conflicts with macOS ControlCenter / AirPlay Receiver on port 5000.
- **Docker Compose Memory Limit:** Standalone Apache Hive 4.0 container capped at `3g` memory limit in `docker-compose.hive.yml`.
