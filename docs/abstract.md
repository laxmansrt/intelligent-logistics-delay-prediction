# Project Abstract

**Project Title:** Intelligent Logistics Delay Prediction Using Big Data Analytics  
**Course:** Big Data Technologies (BDT)  
**Domain:** Distributed Data Engineering & Applied Machine Learning  

---

### Abstract

Supply chain and freight transportation networks form the backbone of modern global commerce. However, operational unpredictability—stemming from highway traffic congestion, adverse weather patterns, vehicle breakdowns, and inefficient dispatch scheduling—frequently leads to delivery delays that inflate operational costs and diminish customer satisfaction. Traditional logistics systems rely on centralized, relational databases that struggle to handle the high velocity, volume, and heterogeneity of multi-source supply chain data such as GPS telematics, real-time traffic updates, and meteorological observations.

This project presents an end-to-end Big Data Technologies platform titled **"Intelligent Logistics Delay Prediction Using Big Data Analytics"**. The platform integrates distributed big data storage, scalable batch processing, and machine learning into a unified web-based intelligence architecture:

1. **Storage Tier:** Implements a dual-mode storage abstraction layer supporting both Apache Hadoop Distributed File System (HDFS) and local directory mirroring, organizing data into raw, processed, and analytical tiers.
2. **Distributed Processing Tier:** Uses Apache Hadoop Streaming MapReduce for distributed multi-dimensional key-value batch aggregations across 390+ logistics dimensions. In parallel, Apache Spark (PySpark) executes in-memory DataFrames for multi-source ETL, deduplication, schema enforcement, and bottleneck route identification.
3. **NoSQL Document Database:** Uses MongoDB to manage semi-structured shipment records, temporal traffic logs, spatial GPS coordinates, job execution logs, and predictive telemetry.
4. **Machine Learning Pipeline:** Employs Scikit-learn with rigorous zero-target-leakage preprocessing to train and compare a Baseline Linear Classifier (Logistic Regression) against an Ensemble Tree Model (Random Forest Classifier). The model predicts binary delay outcomes, calculates risk categories (Low, Medium, High), and surfaces contextual operational contributing factors.
5. **Interactive Analytics Dashboard:** A responsive web application developed using Flask, HTML5, CSS3, JavaScript, and Chart.js that provides logistics operators with real-time KPI overviews, route risk assessments, delay reason distributions, interactive dispatch simulations, and distributed job execution telemetry.

The entire system is engineered for reproducible, zero-cost deployment on commodity hardware (macOS / Linux / Windows) with practical local execution, while retaining full compatibility with distributed enterprise Hadoop and Spark clusters.

