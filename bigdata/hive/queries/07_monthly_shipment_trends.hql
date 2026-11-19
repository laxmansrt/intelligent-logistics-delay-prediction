-- Query 7: Monthly Shipment and Delay Trends
-- Evaluates seasonal shipment volume variations and monthly delay ratios over time.

USE transportation_logistics_db;

SELECT 
    DATE_FORMAT(scheduled_pickup, 'yyyy-MM') AS shipment_month,
    COUNT(shipment_id) AS total_shipments,
    SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) AS delayed_shipments,
    SUM(CASE WHEN is_delayed = 0 THEN 1 ELSE 0 END) AS on_time_shipments,
    ROUND(SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(shipment_id), 2) AS delay_percentage,
    ROUND(AVG(delivery_duration_hours), 1) AS avg_delivery_hours
FROM shipments_orc
WHERE scheduled_pickup IS NOT NULL
GROUP BY DATE_FORMAT(scheduled_pickup, 'yyyy-MM')
ORDER BY shipment_month ASC;

