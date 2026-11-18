"""
tests/test_phase3_bigdata_ml.py
================================
Tests for Big Data Processing (MapReduce & Spark) and Machine Learning modules.

Run with:
    python -m pytest tests/test_phase3_bigdata_ml.py -v
"""

import sys
import io
import json
from pathlib import Path
import pytest
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Config


# ── Fixtures ───────────────────────────────────────────────
@pytest.fixture(scope="module")
def client():
    from backend.app import create_app
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── 1. MapReduce Tests ────────────────────────────────────
class TestMapReduce:
    def test_mapreduce_pipeline_execution(self):
        from bigdata.mapreduce.run_mapreduce import run_mapreduce_job
        sample_csv = Config.DATA_DIR / "sample" / "sample_shipments.csv"
        res = run_mapreduce_job(sample_csv)
        assert res["success"] is True
        assert res["records_aggregated"] > 0
        assert "results" in res
        assert len(res["results"]) > 0

    def test_mapreduce_categories_emitted(self):
        from bigdata.mapreduce.run_mapreduce import run_mapreduce_job
        sample_csv = Config.DATA_DIR / "sample" / "sample_shipments.csv"
        res = run_mapreduce_job(sample_csv)
        categories = {r["category"] for r in res["results"]}
        assert "route" in categories
        assert "carrier" in categories
        assert "vehicle" in categories
        assert "overall" in categories


# ── 2. Big Data Spark/Processing Tests ────────────────────
class TestBigDataProcessing:
    def test_shipment_etl_processor(self):
        from bigdata.spark.shipment_processor import process_shipments
        sample_csv = Config.DATA_DIR / "sample" / "sample_shipments.csv"
        res = process_shipments(sample_csv)
        assert res["success"] is True
        assert res["final_records"] > 0
        assert Path(res["output_path"]).exists()

    def test_route_analyzer(self):
        from bigdata.spark.route_analyzer import analyze_routes
        res = analyze_routes()
        assert res["success"] is True
        assert res["total_routes_analyzed"] > 0
        assert len(res["top_high_risk_routes"]) > 0
        assert Path(res["output_path"]).exists()

    def test_delay_aggregator(self):
        from bigdata.spark.delay_aggregator import aggregate_delay_statistics
        res = aggregate_delay_statistics()
        assert res["success"] is True
        assert "kpis" in res
        assert res["kpis"]["total_shipments"] > 0
        assert len(res["by_carrier"]) > 0
        assert len(res["by_vehicle"]) > 0


# ── 3. Machine Learning Pipeline Tests ─────────────────────
class TestMachineLearning:
    def test_feature_engineering_no_target_leakage(self):
        from ml.feature_engineering import prepare_features_and_target, ALL_FEATURE_COLS
        sample_csv = Config.DATA_DIR / "sample" / "sample_shipments.csv"
        df = pd.read_csv(sample_csv, nrows=10)
        X, y = prepare_features_and_target(df)

        # Ensure excluded leakage columns are NOT in features
        for leakage_col in ["actual_delivery", "actual_pickup", "delay_minutes", "delay_reason", "status"]:
            assert leakage_col not in X.columns, f"Target leakage detected: {leakage_col} in features!"

        assert list(X.columns) == ALL_FEATURE_COLS
        assert len(y) == len(X)

    def test_model_training_and_evaluation(self):
        from ml.train_model import train_delay_model
        report = train_delay_model()
        assert "baseline_model" in report
        assert "primary_model" in report

        # Accuracy must be a valid percentage between 0 and 1
        assert 0.0 <= report["baseline_model"]["accuracy"] <= 1.0
        assert 0.0 <= report["primary_model"]["accuracy"] <= 1.0

        # Confusion matrix must be 2x2
        cm = report["primary_model"]["confusion_matrix"]
        assert len(cm) == 2 and len(cm[0]) == 2

    def test_single_shipment_prediction(self):
        from ml.predict import predict_single_shipment
        sample = {
            "shipment_id": "TEST-100",
            "origin_city": "Mumbai",
            "destination_city": "Delhi",
            "distance_km": 1420.0,
            "weight_kg": 300.0,
            "vehicle_type": "Truck",
            "carrier": "BlueDart",
            "category": "Electronics",
            "scheduled_hour": 8,
        }
        res = predict_single_shipment(sample)
        assert res["is_delayed_predicted"] in (0, 1)
        assert res["delay_risk"] in ("Low", "Medium", "High")
        assert 0.0 <= res["confidence"] <= 1.0
        assert len(res["contributing_factors"]) > 0


# ── 4. API Endpoint Integration Tests ──────────────────────
class TestAPIEndpoints:
    def test_predict_endpoint(self, client):
        payload = {
            "origin_city": "Delhi",
            "destination_city": "Bangalore",
            "distance_km": 2100.0,
            "weight_kg": 500.0,
            "vehicle_type": "Truck",
            "carrier": "Delhivery",
            "category": "Perishables",
            "scheduled_hour": 9,
        }
        resp = client.post("/api/v1/predict", json=payload)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert "delay_risk" in data["data"]

    def test_shipments_list_endpoint(self, client):
        resp = client.get("/api/v1/shipments?per_page=5")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert len(data["data"]) <= 5

    def test_kpi_summary_endpoint(self, client):
        resp = client.get("/api/v1/shipments/stats/summary")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert "total_shipments" in data["data"]

    def test_analytics_endpoints(self, client):
        for ep in ["delay-reasons", "carrier-performance", "vehicle-performance", "model-metrics"]:
            resp = client.get(f"/api/v1/analytics/{ep}")
            assert resp.status_code == 200
            assert resp.get_json()["success"] is True

    def test_jobs_run_mapreduce_endpoint(self, client):
        resp = client.post("/api/v1/jobs/mapreduce/run")
        assert resp.status_code == 200
        assert resp.get_json()["success"] is True

    def test_frontend_pages_render(self, client):
        pages = ["/", "/shipments-page", "/predict-page", "/analytics-page", "/processing-page", "/model-page", "/upload-page"]
        for p in pages:
            resp = client.get(p)
            assert resp.status_code == 200
            assert b"<!DOCTYPE html>" in resp.data or b"html" in resp.data.lower()

