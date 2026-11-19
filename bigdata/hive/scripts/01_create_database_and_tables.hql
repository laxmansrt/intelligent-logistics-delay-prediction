-- =============================================================================
-- Script: 01_create_database_and_tables.hql
-- Project: Big Data Classification and Prediction for Transportation and Logistics using Apache Hive
-- =============================================================================
-- Description:
-- Creates the dedicated transportation and logistics database in Apache Hive,
-- an external raw staging table, an optimized ORC managed table with partitioning,
-- and aggregate analytics tables.
-- =============================================================================

-- Step 1: Create Database
CREATE DATABASE IF NOT EXISTS transportation_logistics_db
COMMENT 'Enterprise Big Data Warehouse for Transportation and Logistics Analytics'
LOCATION '/user/hive/warehouse/transportation_logistics.db';

USE transportation_logistics_db;

-- Step 2: Create Raw External Table (Schema-on-Read over CSV)
DROP TABLE IF EXISTS shipments_raw;

CREATE EXTERNAL TABLE IF NOT EXISTS shipments_raw (
    shipment_id          STRING COMMENT 'Unique shipment identifier (e.g. SHP-20230101-0001)',
    origin_city          STRING COMMENT 'Origin / Departure City',
    origin_state         STRING COMMENT 'Origin State/Province',
    origin_lat           DOUBLE COMMENT 'Origin Latitude',
    origin_lon           DOUBLE COMMENT 'Origin Longitude',
    destination_city     STRING COMMENT 'Destination / Arrival City',
    destination_state    STRING COMMENT 'Destination State/Province',
    destination_lat      DOUBLE COMMENT 'Destination Latitude',
    destination_lon      DOUBLE COMMENT 'Destination Longitude',
    distance_km          DOUBLE COMMENT 'Highway transit distance in kilometers',
    transportation_mode  STRING COMMENT 'Mode of transit: Truck, Van, Mini-Truck, Rail, Air Cargo',
    carrier              STRING COMMENT 'Logistics Carrier Company',
    weight_kg            DOUBLE COMMENT 'Gross cargo weight in kilograms',
    category             STRING COMMENT 'Commodity category (Electronics, Food, Perishables, etc.)',
    scheduled_pickup     STRING COMMENT 'Scheduled pickup ISO 8601 timestamp',
    actual_pickup        STRING COMMENT 'Actual pickup ISO 8601 timestamp',
    scheduled_delivery   STRING COMMENT 'Scheduled delivery ISO 8601 timestamp',
    actual_delivery      STRING COMMENT 'Actual delivery ISO 8601 timestamp',
    is_delayed           INT    COMMENT 'Classification target: 0 = On-Time, 1 = Delayed',
    delay_minutes        DOUBLE COMMENT 'Transit delay duration in minutes',
    delay_reason         STRING COMMENT 'Operational contributor to delay',
    status               STRING COMMENT 'Lifecycle status: Delivered, In Transit, Pending',
    data_source          STRING COMMENT 'Data provenance label'
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/logistics/hive/raw/shipments'
TBLPROPERTIES (
    "skip.header.line.count"="1",
    "serialization.null.format"=""
);

-- Step 3: Create Optimized Managed Table (Columnar ORC with Partitioning)
-- BDT Concept: Columnar ORC provides predicate pushdown, vectorization, and high compression.
DROP TABLE IF EXISTS shipments_orc;

CREATE TABLE IF NOT EXISTS shipments_orc (
    shipment_id          STRING,
    origin_city          STRING,
    origin_state         STRING,
    origin_lat           DOUBLE,
    origin_lon           DOUBLE,
    destination_city     STRING,
    destination_state    STRING,
    destination_lat      DOUBLE,
    destination_lon      DOUBLE,
    distance_km          DOUBLE,
    carrier              STRING,
    weight_kg            DOUBLE,
    category             STRING,
    scheduled_pickup     TIMESTAMP,
    actual_pickup        TIMESTAMP,
    scheduled_delivery   TIMESTAMP,
    actual_delivery      TIMESTAMP,
    is_delayed           INT,
    delay_minutes        DOUBLE,
    delay_reason         STRING,
    status               STRING,
    delivery_duration_hours DOUBLE COMMENT 'Computed transit duration from actual pickup to delivery'
)
PARTITIONED BY (
    transportation_mode STRING COMMENT 'Partitioning key: Truck, Van, Rail, Air Cargo'
)
STORED AS ORC
TBLPROPERTIES (
    "orc.compress"="SNAPPY",
    "orc.create.index"="true"
);

-- Step 4: Route Delay Analytics Summary Table
DROP TABLE IF EXISTS route_delay_summary;

CREATE TABLE IF NOT EXISTS route_delay_summary (
    route_key           STRING,
    origin_city         STRING,
    destination_city    STRING,
    total_shipments     BIGINT,
    on_time_count       BIGINT,
    delayed_count       BIGINT,
    delay_percentage    DOUBLE,
    avg_delay_minutes   DOUBLE,
    avg_distance_km     DOUBLE,
    risk_category       STRING
)
STORED AS ORC;

