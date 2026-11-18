/**
 * frontend/static/js/main.js
 * ===========================
 * Global UI helpers and dynamic system status polling.
 */

document.addEventListener("DOMContentLoaded", async () => {
    // Check system status and update topbar badges
    try {
        const res = await fetch("/api/v1/health/detail");
        const json = await res.json();
        if (json.success && json.data) {
            const comp = json.data.components;
            const storageBadge = document.getElementById("sys-storage");
            const sparkBadge = document.getElementById("sys-spark");

            if (storageBadge && comp.storage) {
                storageBadge.innerText = `Storage: ${comp.storage.mode.toUpperCase()}`;
                storageBadge.className = comp.storage.mode === "hdfs" ? "badge badge-success" : "badge badge-info";
            }

            if (sparkBadge && comp.spark) {
                sparkBadge.innerText = `Spark: ${comp.spark.master}`;
                sparkBadge.className = "badge badge-success";
            }
        }
    } catch (e) {
        console.warn("Health check unreachable", e);
    }
});

