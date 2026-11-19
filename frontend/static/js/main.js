/**
 * frontend/static/js/main.js
 * ===========================
 * Global UI helpers and dynamic system status polling.
 * Project: Big Data Classification and Prediction for Transportation and Logistics using Apache Hive
 */

document.addEventListener("DOMContentLoaded", async () => {
    // Check system status and update topbar badges
    try {
        const res = await fetch("/api/v1/health/detail");
        const json = await res.json();
        if (json.success && json.data) {
            const comp = json.data.components;
            const storageBadge = document.getElementById("sys-storage");

            if (storageBadge && comp.storage) {
                storageBadge.innerText = `Storage: ${comp.storage.mode.toUpperCase()}`;
                storageBadge.className = comp.storage.mode === "hdfs" ? "badge badge-success" : "badge badge-info";
            }
        }
    } catch (e) {
        console.warn("Health check unreachable", e);
    }

    // Check Hive status
    try {
        const res = await fetch("/api/v1/hive/status");
        const json = await res.json();
        const hiveBadge = document.getElementById("sys-hive");
        if (hiveBadge && json.success && json.data) {
            if (json.data.hive_connected) {
                hiveBadge.innerText = `🐝 Hive: ${json.data.database_name} (${json.data.table_count} tables)`;
                hiveBadge.className = "badge badge-success";
            } else {
                hiveBadge.innerText = "🐝 Hive: Offline";
                hiveBadge.className = "badge badge-warning";
            }
        }
    } catch (e) {
        console.warn("Hive status check failed", e);
    }
});
