"""
tests/test_phase4_hive.py
=========================
Automated tests for Apache Hive integration, HiveQL analytical queries,
and Hive REST API endpoints.

Official Project:
    "Big Data Classification and Prediction for Transportation and Logistics using Apache Hive"

Run with:
    python -m pytest tests/test_phase4_hive.py -v
"""

import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="module")
def client():
    from backend.app import create_app
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestApacheHiveService:
    """Tests Hive service methods, table creation, and HiveQL execution."""

    def test_hive_status(self):
        from backend.services.hive_service import hive_service
        status = hive_service.get_hive_status()
        assert "hive_connected" in status
        assert "database_name" in status
        assert status["database_name"] == "transportation_logistics_db"

    def test_hive_schema_initialization(self):
        from backend.services.hive_service import hive_service
        report = hive_service.initialize_hive_schema()
        assert report["success"] is True
        assert report["database"] == "transportation_logistics_db"
        assert report["table"] == "shipments_orc"
        assert report["records_loaded"] > 0

    def test_hiveql_query_total_shipments(self):
        from backend.services.hive_service import hive_service
        res = hive_service.run_named_query("total_shipments")
        assert res["success"] is True
        assert "total_shipments" in res["columns"]
        assert len(res["rows"]) == 1
        assert res["rows"][0][0] > 0

    def test_hiveql_query_ontime_vs_delayed(self):
        from backend.services.hive_service import hive_service
        res = hive_service.run_named_query("ontime_vs_delayed")
        assert res["success"] is True
        assert "classification_status" in res["columns"]
        statuses = [r[0] for r in res["rows"]]
        assert "Delayed" in statuses or "On-Time" in statuses

    def test_hiveql_query_delay_percentage(self):
        from backend.services.hive_service import hive_service
        res = hive_service.run_named_query("delay_percentage")
        assert res["success"] is True
        assert "delay_percentage" in res["columns"]
        assert len(res["rows"]) == 1

    def test_hiveql_query_avg_delivery_duration(self):
        from backend.services.hive_service import hive_service
        res = hive_service.run_named_query("avg_delivery_duration")
        assert res["success"] is True
        assert "avg_duration_hours" in res["columns"]
        assert len(res["rows"]) > 0

    def test_hiveql_query_routes_highest_delays(self):
        from backend.services.hive_service import hive_service
        res = hive_service.run_named_query("routes_highest_delays")
        assert res["success"] is True
        assert "route_corridor" in res["columns"]
        assert "risk_tier" in res["columns"]
        assert len(res["rows"]) > 0

    def test_hiveql_query_transportation_mode_analysis(self):
        from backend.services.hive_service import hive_service
        res = hive_service.run_named_query("transportation_mode_analysis")
        assert res["success"] is True
        assert "transportation_mode" in res["columns"]
        assert len(res["rows"]) > 0

    def test_hiveql_query_monthly_trends(self):
        from backend.services.hive_service import hive_service
        res = hive_service.run_named_query("monthly_shipment_trends")
        assert res["success"] is True
        assert "shipment_month" in res["columns"]
        assert len(res["rows"]) > 0

    def test_custom_hiveql_execution(self):
        from backend.services.hive_service import hive_service
        res = hive_service.execute_hiveql("SELECT COUNT(*) AS cnt FROM shipments_orc")
        assert res["success"] is True
        assert res["columns"] == ["cnt"]
        assert res["rows"][0][0] > 0


class TestHiveAPIEndpoints:
    """Tests Hive REST API routes and template rendering."""

    def test_api_hive_status(self, client):
        resp = client.get("/api/v1/hive/status")
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert json_data["success"] is True
        assert "database_name" in json_data["data"]

    def test_api_hive_scripts_list(self, client):
        resp = client.get("/api/v1/hive/scripts")
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert json_data["success"] is True
        assert json_data["data"]["count"] == 7

    def test_api_hive_named_query_endpoint(self, client):
        resp = client.get("/api/v1/hive/query/ontime_vs_delayed")
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert json_data["success"] is True
        assert "columns" in json_data["data"]
        assert "rows" in json_data["data"]

    def test_api_hive_custom_query_endpoint(self, client):
        resp = client.post("/api/v1/hive/query", json={"query": "SELECT COUNT(*) AS total FROM shipments_orc"})
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert json_data["success"] is True

    def test_hive_page_template_renders(self, client):
        resp = client.get("/hive-page")
        assert resp.status_code == 200
        assert b"Apache Hive" in resp.data
        assert b"HiveQL" in resp.data
