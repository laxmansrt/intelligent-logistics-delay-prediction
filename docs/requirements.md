# Software & Hardware Requirements

### 1. Hardware Requirements

#### Minimum Development Machine (Student Local Mode)
- **Processor:** Dual-Core 64-bit CPU (x86_64 or Apple Silicon ARM64, e.g. M1/M2/M3)
- **RAM:** 4 GB Minimum (8 GB recommended for simultaneous Spark and browser execution)
- **Disk Space:** 2 GB free disk space for Python virtual environment, dependencies, sample datasets, and model binaries
- **Network:** Standard internet access for initial dependency installations

#### Optional Enterprise Cluster Environment (Multi-Node BDT Deployment)
- **Master Node:** 4-8 CPU Cores, 16 GB RAM (runs Hadoop NameNode, YARN ResourceManager, Spark Master)
- **Worker Nodes (x3):** 4-8 CPU Cores, 16 GB RAM each (run HDFS DataNodes, YARN NodeManagers, Spark Workers)
- **Network Fabric:** 1 Gbps / 10 Gbps Ethernet

---

### 2. Software Requirements

#### Operating System Compatibility
- **macOS:** macOS Monterey (12.0) through macOS Sonoma / Sequoia (fully supported and verified)
- **Linux:** Ubuntu 20.04+, Debian 11+, RHEL/CentOS 8+
- **Windows:** Windows 10/11 with WSL2 (Windows Subsystem for Linux) or standard Python 3.11+

#### Runtimes & Compilers
- **Python:** Python 3.10, 3.11, 3.12, or 3.14 (Verified working on Python 3.14.3)
- **Java:** Java Runtime Environment (JRE) / JDK 11 or higher (OpenJDK 11+ required for Apache Spark)

#### Database
- **MongoDB:** MongoDB Community Server 6.x or 7.x (Optional — local fallback supported if offline)

#### Core Python Packages & Libraries
```text
flask==3.0.3          # Web framework & REST API
flask-cors==4.0.0     # Cross-Origin Resource Sharing
pymongo==4.7.2        # MongoDB official driver
pandas==2.2.2         # Data wrangling & tabular operations
numpy>=1.24.1         # Vectorized array computations
pyspark>=3.5.0        # Distributed in-memory data processing
scikit-learn>=1.5.0   # Machine learning modeling & metrics
joblib>=1.4.0         # Model serialization & pipeline persistence
python-dotenv==1.0.1  # 12-factor environment configuration
pytest>=8.0.0         # Unit, API, and pipeline test suite
```

#### Frontend Web Technologies
- **HTML5:** Semantic document markup
- **CSS3:** Custom responsive layout, CSS variables, dark-navy theme
- **JavaScript (ES6+):** Asynchronous `fetch` calls, dynamic DOM manipulation
- **Chart.js (v4.x):** Responsive HTML5 Canvas data visualizations

