-- Query 4: Average Delivery Duration
-- Computes the mean delivery transit duration (in hours) grouped by transportation mode and overall.

USE transportation_logistics_db;

SELECT 
    COALESCE(transportation_mode, 'ALL MODES') AS transportation_mode,
    COUNT(shipment_id) AS shipment_count,
    ROUND(AVG(delivery_duration_hours), 2) AS avg_duration_hours,
    ROUND(AVG(delivery_duration_hours) / 24.0, 2) AS avg_duration_days,
    ROUND(AVG(distance_km), 1) AS avg_distance_km
FROM shipments_orc
GROUP BY transportation_mode
WITH CUBE
ORDER BY avg_duration_hours DESC;

