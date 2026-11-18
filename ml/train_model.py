"""
ml/train_model.py
=================
Machine Learning Training Pipeline for Logistics Delay Prediction.

Models evaluated:
1. Baseline: Logistic Regression (linear classification benchmark)
2. Primary Model: Random Forest Classifier (ensemble tree model)

BDT Concept:
    Reproducible ML workflow with automated feature preprocessing,
    train/test stratified splitting, hyperparameter control,
    and objective metric logging (No fabricated results!).
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import Config
from backend.utils.logger import get_logger
from ml.feature_engineering import (
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
    prepare_features_and_target,
)

logger = get_logger(__name__)


def train_delay_model(
    data_path: str | Path | None = None,
    model_output_dir: str | Path | None = None,
) -> Dict[str, Any]:
    """
    Train and evaluate delay prediction models.

    Returns:
        Evaluation report dict containing real test metrics for both models.
    """
    start_time = datetime.now(timezone.utc)

    # 1. Scikit-learn imports
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler, OneHotEncoder
        from sklearn.compose import ColumnTransformer
        from sklearn.pipeline import Pipeline
        from sklearn.linear_model import LogisticRegression
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
        )
        import joblib
    except ImportError as e:
        logger.error("Scikit-learn / joblib not available: %s", e)
        raise RuntimeError("Install scikit-learn and joblib to train ML models.") from e

    # 2. Load dataset
    if data_path is None:
        # Check processed clean data first, then fallback to sample
        clean_file = Config.DATA_DIR / "processed" / "shipments_clean" / "clean_shipments.csv"
        data_path = clean_file if clean_file.exists() else Config.DATA_DIR / "sample" / "sample_shipments.csv"

    data_file = Path(data_path)
    if not data_file.exists():
        raise FileNotFoundError(f"Training data not found at: {data_file}")

    if model_output_dir is None:
        model_output_dir = Config.DATA_DIR / "models"
    out_dir = Path(model_output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Loading training data from %s", data_file)
    df = pd.read_csv(data_file)
    X, y = prepare_features_and_target(df)

    # 3. Stratified Train/Test Split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=Config.RANDOM_STATE,
        stratify=y if len(np.unique(y)) > 1 else None,
    )
    logger.info("Dataset split: %d train samples, %d test samples", len(X_train), len(X_test))

    # 4. Feature Preprocessing Pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
        ]
    )

    # 5. Baseline Model: Logistic Regression
    lr_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=500, random_state=Config.RANDOM_STATE)),
    ])
    lr_pipeline.fit(X_train, y_train)
    y_pred_lr = lr_pipeline.predict(X_test)

    baseline_metrics = {
        "model_name": "LogisticRegression (Baseline)",
        "accuracy": round(float(accuracy_score(y_test, y_pred_lr)), 4),
        "precision": round(float(precision_score(y_test, y_pred_lr, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred_lr, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred_lr, zero_division=0)), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred_lr).tolist(),
    }

    # 6. Primary Model: Random Forest Classifier
    rf_pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            random_state=Config.RANDOM_STATE,
            n_jobs=1,
        )),
    ])
    rf_pipeline.fit(X_train, y_train)
    y_pred_rf = rf_pipeline.predict(X_test)

    # Extract Feature Importances from Random Forest
    rf_classifier = rf_pipeline.named_steps["classifier"]
    encoded_cat_names = rf_pipeline.named_steps["preprocessor"].transformers_[1][1].get_feature_names_out(CATEGORICAL_FEATURES)
    all_feature_names = list(NUMERIC_FEATURES) + list(encoded_cat_names)
    importances = rf_classifier.feature_importances_

    # Map back to top 10 important features
    top_indices = np.argsort(importances)[::-1][:10]
    top_features = {all_feature_names[i]: round(float(importances[i]), 4) for i in top_indices}

    primary_metrics = {
        "model_name": "RandomForestClassifier",
        "version": Config.MODEL_VERSION,
        "accuracy": round(float(accuracy_score(y_test, y_pred_rf)), 4),
        "precision": round(float(precision_score(y_test, y_pred_rf, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred_rf, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, y_pred_rf, zero_division=0)), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred_rf).tolist(),
        "top_feature_importances": top_features,
        "hyperparameters": {
            "n_estimators": 100,
            "max_depth": 12,
            "random_state": Config.RANDOM_STATE,
        },
    }

    # 7. Persist Best Model (Random Forest)
    model_file = out_dir / "delay_predictor.joblib"
    joblib.dump(rf_pipeline, model_file)
    logger.info("Saved trained model pipeline to %s", model_file)

    # 8. Save Metrics JSON
    evaluation_summary = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset_size": len(df),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "baseline_model": baseline_metrics,
        "primary_model": primary_metrics,
        "duration_seconds": round((datetime.now(timezone.utc) - start_time).total_seconds(), 2),
    }

    metrics_file = out_dir / "evaluation_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(evaluation_summary, f, indent=2)

    # 9. Log into MongoDB model_metrics collection if available
    try:
        from backend.extensions import get_collection
        metrics_col = get_collection("model_metrics")
        metrics_col.insert_one(evaluation_summary.copy())
    except Exception:
        pass

    logger.info(
        "ML Training Complete. RF Accuracy: %.2f%%, F1: %.4f (Baseline Acc: %.2f%%)",
        primary_metrics["accuracy"] * 100,
        primary_metrics["f1_score"],
        baseline_metrics["accuracy"] * 100,
    )

    return evaluation_summary


if __name__ == "__main__":
    report = train_delay_model()
    print("Training Report Summary:")
    print("Baseline:", report["baseline_model"])
    print("Primary:", report["primary_model"])
