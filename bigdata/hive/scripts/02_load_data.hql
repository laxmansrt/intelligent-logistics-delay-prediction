-- =============================================================================
-- Script: 02_load_data.hql
-- Project: Big Data Classification and Prediction for Transportation and Logistics using Apache Hive
-- =============================================================================
-- Description:
-- Ingests raw CSV data into shipments_raw and performs a distributed
-- transformation into the partitioned ORC table shipments_orc with dynamic partitioning.
-- =============================================================================

USE transportation_logistics_db;

-- Step 1: Configure Dynamic Partitioning Settings
SET hive.exec.dynamic.partition = true;
SET hive.exec.dynamic.partition.mode = nonstrict;
SET hive.exec.max.dynamic.partitions = 1000;
SET hive.exec.max.dynamic.partitions.pernode = 250;
SET hive.optimize.sort.dynamic.partition = true;

-- Step 2: Load Raw CSV into Staging Table
-- (When running in cluster: path points to HDFS; in local mode points to local filesystem)
-- LOAD DATA LOCAL INPATH '/data/sample/sample_shipments.csv' OVERWRITE INTO TABLE shipments_raw;

-- Step 3: Populate Managed Partitioned ORC Table with Data Type Conversions & Preprocessing
INSERT OVERWRITE TABLE shipments_orc PARTITION (transportation_mode)
SELECT
    shipment_id,
    origin_city,
    origin_state,
    origin_lat,
    origin_lon,
    destination_city,
    destination_state,
    destination_lat,
    destination_lon,
    distance_km,
    carrier,
    weight_kg,
    category,
    CAST(scheduled_pickup AS TIMESTAMP) AS scheduled_pickup,
    CAST(actual_pickup AS TIMESTAMP) AS actual_pickup,
    CAST(scheduled_delivery AS TIMESTAMP) AS scheduled_delivery,
    CAST(actual_delivery AS TIMESTAMP) AS actual_delivery,
    -- Target variable validation:
    -- Delayed = 1 if actual delivery is strictly later than scheduled delivery, else 0
    CASE
        WHEN CAST(actual_delivery AS TIMESTAMP) > CAST(scheduled_delivery AS TIMESTAMP) THEN 1
        WHEN is_delayed = 1 THEN 1
        ELSE 0
    END AS is_delayed,
    COALESCE(delay_minutes, 0.0) AS delay_minutes,
    COALESCE(delay_reason, 'No Delay') AS delay_reason,
    COALESCE(status, 'Delivered') AS status,
    -- Compute transit duration in hours
    ROUND((UNIX_TIMESTAMP(CAST(actual_delivery AS TIMESTAMP)) - UNIX_TIMESTAMP(CAST(actual_pickup AS TIMESTAMP))) / 3600.0, 2) AS delivery_duration_hours,
    -- Partition key placed as the last selected column for dynamic partitioning
    COALESCE(transportation_mode, 'Truck') AS transportation_mode
FROM shipments_raw
WHERE shipment_id IS NOT NULL AND shipment_id != 'shipment_id';

