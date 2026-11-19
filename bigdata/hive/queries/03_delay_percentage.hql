-- Query 3: Delay Percentage & Duration Analytics
-- Evaluates system-wide delay frequency, mean delay duration, and max delay.

USE transportation_logistics_db;

SELECT 
    COUNT(shipment_id) AS total_shipments,
    SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) AS delayed_shipments,
    SUM(CASE WHEN is_delayed = 0 THEN 1 ELSE 0 END) AS on_time_shipments,
    ROUND(SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(shipment_id), 2) AS delay_percentage,
    ROUND(AVG(CASE WHEN is_delayed = 1 THEN delay_minutes ELSE NULL END), 2) AS avg_delay_minutes,
    ROUND(MAX(delay_minutes), 1) AS max_delay_minutes
FROM shipments_orc;

