-- Query 1: Total Number of Shipments
-- Computes global total volume of shipments recorded in the Apache Hive warehouse.

USE transportation_logistics_db;

SELECT 
    COUNT(shipment_id) AS total_shipments,
    COUNT(DISTINCT origin_city) AS total_origin_cities,
    COUNT(DISTINCT destination_city) AS total_destination_cities,
    COUNT(DISTINCT carrier) AS total_carriers
FROM shipments_orc;

