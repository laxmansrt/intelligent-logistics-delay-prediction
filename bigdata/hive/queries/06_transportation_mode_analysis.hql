-- Query 6: Shipment Analysis by Transportation Mode
-- Analyzes delay susceptibility, volume, and average distance across freight transport modes.

USE transportation_logistics_db;

SELECT 
    transportation_mode,
    COUNT(shipment_id) AS total_shipments,
    SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) AS delayed_count,
    ROUND(SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(shipment_id), 2) AS delay_percentage,
    ROUND(AVG(distance_km), 1) AS avg_distance_km,
    ROUND(AVG(weight_kg), 1) AS avg_weight_kg,
    ROUND(AVG(delivery_duration_hours), 1) AS avg_transit_hours
FROM shipments_orc
GROUP BY transportation_mode
ORDER BY delay_percentage DESC;

