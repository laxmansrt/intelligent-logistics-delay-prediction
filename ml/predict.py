"""
ml/predict.py
=============
Inference Service for Real-time Logistics Delay Prediction.

BDT Concept:
    Operationalizes the trained ML pipeline to provide low-latency
    predictions on new/unseen shipment requests.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Config
from backend.utils.logger import get_logger
from ml.feature_engineering import prepare_features_and_target, ALL_FEATURE_COLS

logger = get_logger(__name__)

_model_cache = None


def load_model(model_path: str | Path | None = None):
    """Load and cache the trained ML pipeline."""
    global _model_cache

    if _model_cache is not None:
        return _model_cache

    import joblib

    if model_path is None:
        model_path = Config.DATA_DIR / "models" / "delay_predictor.joblib"

    path = Path(model_path)
    if not path.exists():
        logger.warning("Trained model not found at %s. Triggering training...", path)
        from ml.train_model import train_delay_model
        train_delay_model()

    if not path.exists():
        raise FileNotFoundError(f"Model file {path} not found.")

    _model_cache = joblib.load(path)
    logger.info("Loaded delay prediction model from %s", path)
    return _model_cache


def predict_single_shipment(shipment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict delay probability, risk category, and contributing factors for a single shipment.

    Args:
        shipment_data: dict with fields e.g.:
            origin_city, destination_city, distance_km, weight_kg,
            vehicle_type, carrier, category, scheduled_hour, etc.

    Returns:
        dict with prediction results:
        - is_delayed_predicted (0 | 1)
        - delay_risk ("Low" | "Medium" | "High")
        - confidence (float between 0 and 1)
        - delay_probability (float)
        - contributing_factors (list of explanatory strings)
    """
    model = load_model()

    df_input = pd.DataFrame([shipment_data])
    X, _ = prepare_features_and_target(df_input)

    # Probability of delay (class 1)
    probabilities = model.predict_proba(X)[0]
    delay_prob = float(probabilities[1]) if len(probabilities) > 1 else 0.0

    # Binary prediction
    is_delayed = int(delay_prob >= 0.50)

    # Risk Categorization
    if delay_prob >= 0.65:
        risk_category = "High"
    elif delay_prob >= 0.35:
        risk_category = "Medium"
    else:
        risk_category = "Low"

    # Rule-based contributing factor explanation
    factors = []
    dist = float(shipment_data.get("distance_km", 0.0))
    if dist > 1400:
        factors.append(f"Long-haul route distance ({dist:.0f} km) increases transit vulnerability")
    elif dist > 800:
        factors.append(f"Moderate transit distance ({dist:.0f} km)")

    vtype = str(shipment_data.get("vehicle_type", ""))
    if vtype.lower() == "truck":
        factors.append("Road freight (Truck) subject to highway congestion")

    hour = int(shipment_data.get("scheduled_hour", 10))
    if (7 <= hour <= 10) or (17 <= hour <= 20):
        factors.append(f"Departure scheduled during peak traffic hours ({hour:02d}:00)")

    category = str(shipment_data.get("category", ""))
    if category.lower() in ("perishables", "pharmaceuticals"):
        factors.append(f"Sensitive cargo category ({category}) with strict transit windows")

    if not factors:
        factors.append("Optimal route parameters and standard operating conditions")

    return {
        "shipment_id": shipment_data.get("shipment_id", "ADHOC"),
        "predicted_at": datetime.now(timezone.utc).isoformat(),
        "is_delayed_predicted": is_delayed,
        "delay_probability": round(delay_prob, 4),
        "confidence": round(max(delay_prob, 1.0 - delay_prob), 4),
        "delay_risk": risk_category,
        "contributing_factors": factors,
    }

