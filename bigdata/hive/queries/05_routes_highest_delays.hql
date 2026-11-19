-- Query 5: Routes with the Highest Delay Counts and Rates
-- Identifies top logistical bottleneck corridors by grouping on Origin -> Destination routes.

USE transportation_logistics_db;

SELECT 
    CONCAT(origin_city, ' -> ', destination_city) AS route_corridor,
    COUNT(shipment_id) AS total_dispatches,
    SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) AS delayed_count,
    ROUND(SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(shipment_id), 2) AS delay_rate_pct,
    ROUND(AVG(CASE WHEN is_delayed = 1 THEN delay_minutes ELSE 0.0 END), 1) AS avg_delay_minutes,
    ROUND(AVG(distance_km), 1) AS avg_distance_km,
    CASE 
        WHEN (SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(shipment_id)) >= 45.0 THEN 'HIGH RISK'
        WHEN (SUM(CASE WHEN is_delayed = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(shipment_id)) >= 25.0 THEN 'MEDIUM RISK'
        ELSE 'LOW RISK'
    END AS risk_tier
FROM shipments_orc
GROUP BY origin_city, destination_city
HAVING COUNT(shipment_id) >= 5
ORDER BY delayed_count DESC, delay_rate_pct DESC
LIMIT 15;

