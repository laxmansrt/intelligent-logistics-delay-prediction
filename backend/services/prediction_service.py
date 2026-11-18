"""
backend/services/prediction_service.py
======================================
Service wrapper for ML delay predictions and database persistence.
"""

from typing import Dict, Any, List
import pandas as pd
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class PredictionService:
    """Provides inference methods and logs predictions into MongoDB."""

    def predict_one(self, shipment_dict: Dict[str, Any]) -> Dict[str, Any]:
        from ml.predict import predict_single_shipment
        result = predict_single_shipment(shipment_dict)

        # Log into MongoDB if available
        try:
            from backend.extensions import get_collection
            col = get_collection("prediction_results")
            doc = result.copy()
            doc["input_features"] = shipment_dict
            col.insert_one(doc)
        except Exception:
            pass

        return result

    def predict_batch_df(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        from ml.predict import predict_single_shipment
        records = df.to_dict(orient="records")
        results = []
        for rec in records:
            results.append(self.predict_one(rec))
        return results


prediction_service = PredictionService()

