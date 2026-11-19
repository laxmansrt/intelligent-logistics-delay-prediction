# Problem Statement

**Project Title:** Big Data Classification and Prediction for Transportation and Logistics using Apache Hive

---

### 1. Context & Business Motivation
Modern freight transportation networks generate high-volume, multi-source data streams continuously: vehicle transponder GPS telemetry, highway toll congestion logs, automated weather observations, warehouse handling timestamps, and shipment lifecycle events. Despite this abundance of data, logistics providers frequently suffer from chronic transit schedule deviations.

Empirical studies indicate:
- Over **30% of commercial freight dispatches** experience transit delays exceeding contractual delivery windows.
- Delays compound exponentially across supply chains, triggering warehouse gridlocks, perishable freight spoilage, missed maritime/rail connecting slots, penalty charges, and customer churn.
- Most delays are discovered **reactively** after scheduled delivery deadlines have already passed, rather than anticipated **proactively** at dispatch planning time.

### 2. Limitations of Existing Systems
Traditional logistics management systems (LMS) and enterprise resource planning (ERP) architectures suffer from severe structural bottlenecks:
1. **RDBMS Scalability Ceilings:** Traditional relational databases (MySQL, Oracle) enforce rigid schema-on-write constraints that degrade under millions of historical shipment rows, multi-city weather logs, and high-velocity telematics.
2. **Slow Single-Node Reporting:** SQL reporting queries running on monolithic servers experience exponential query slowdowns, table locks, and memory exhaustion when performing complex analytical aggregations across high-cardinality route corridors.
3. **Absence of Centralized Big Data Warehousing:** Lack of distributed columnar storage (such as Apache Hive ORC) results in redundant full-table scans, inefficient disk I/O, and inability to partition multi-modal transportation datasets effectively.
4. **Purely Reactive Historical Summaries:** Existing tools report *what happened in the past*, but lack statistical intelligence to estimate *whether a pending shipment will be delayed in the future*.
5. **Target Leakage in Naive Machine Learning:** Inexperienced implementations frequently include post-dispatch attributes (such as actual delivery timestamps, actual transit duration, or recorded delay reasons) as inputs when training prediction models, resulting in invalid, artificially inflated accuracy metrics that fail catastrophically in production.

### 3. Problem Definition
To overcome these limitations, there is a clear imperative to develop a scalable Big Data analytics and classification system that can:
- Ingest and store multi-source logistics records across a tiered distributed storage architecture.
- Utilize **Apache Hive** as the central Big Data warehouse to organize data into optimized columnar ORC tables partitioned by transportation mode.
- Execute declarative **HiveQL queries** to classify shipments into On-Time vs. Delayed categories, analyze transit duration patterns, and identify bottleneck routes with high delay frequencies.
- Train machine learning classification models strictly on pre-dispatch features to accurately predict delay likelihood before departure.
- Present these analytical insights and predictions through a responsive, professional web dashboard for real-time decision-making.
