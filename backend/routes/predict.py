"""
backend/routes/predict.py
=========================
API Endpoints for Machine Learning Shipment Delay Predictions.
"""

from flask import Blueprint, request
import pandas as pd
from backend.utils.response import success_response, error_response
from backend.utils.logger import get_logger
from backend.services.prediction_service import prediction_service

logger = get_logger(__name__)
predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/predict", methods=["POST"])
def predict():
    """Predict delay risk for a single shipment JSON payload."""
    data = request.get_json()
    if not data:
        return error_response("Request body must be valid JSON.", status_code=400)

    try:
        prediction = prediction_service.predict_one(data)
        return success_response(data=prediction, message="Prediction calculated successfully.")
    except Exception as exc:
        logger.exception("Prediction endpoint failed")
        return error_response(f"Prediction error: {exc}", status_code=500)


@predict_bp.route("/predictions", methods=["GET"])
def list_predictions():
    """List recent prediction history from MongoDB."""
    limit = int(request.args.get("limit", 20))
    try:
        from backend.extensions import get_collection
        col = get_collection("prediction_results")
        results = list(col.find({}, {"_id": 0}).sort("predicted_at", -1).limit(limit))
        return success_response(data={"predictions": results, "count": len(results)})
    except Exception:
        # Graceful fallback if MongoDB is offline
        return success_response(data={"predictions": [], "count": 0, "note": "Database offline"})


@predict_bp.route("/model/train", methods=["POST"])
def trigger_training():
    """Trigger ML pipeline training and evaluation."""
    try:
        from ml.train_model import train_delay_model
        report = train_delay_model()
        return success_response(data=report, message="Model training completed successfully.")
    except Exception as exc:
        logger.exception("Model training failed")
        return error_response(f"Training failed: {exc}", status_code=500)

