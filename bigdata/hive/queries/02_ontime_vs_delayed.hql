-- Query 2: On-Time Versus Delayed Shipments
-- Classifies shipments into binary categories: On-Time vs Delayed.

USE transportation_logistics_db;

SELECT 
    CASE 
        WHEN is_delayed = 1 THEN 'Delayed'
        ELSE 'On-Time'
    END AS classification_status,
    COUNT(shipment_id) AS total_count,
    ROUND(COUNT(shipment_id) * 100.0 / SUM(COUNT(shipment_id)) OVER(), 2) AS percentage
FROM shipments_orc
GROUP BY is_delayed
ORDER BY total_count DESC;

