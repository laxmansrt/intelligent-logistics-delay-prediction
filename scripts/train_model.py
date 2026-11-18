"""
scripts/train_model.py
======================
CLI script to train and evaluate delay prediction ML models.

Usage:
    python scripts/train_model.py
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.train_model import train_delay_model


def main():
    print("=" * 60)
    print("  LOGISTICS DELAY PREDICTION — MODEL TRAINING")
    print("  Models: Logistic Regression (Baseline) vs Random Forest")
    print("=" * 60)

    report = train_delay_model()

    print("\n--- Model Evaluation Results ---")
    base = report["baseline_model"]
    prim = report["primary_model"]

    print(f"\n[Baseline] {base['model_name']}:")
    print(f"  Accuracy  : {base['accuracy']*100:.2f}%")
    print(f"  Precision : {base['precision']:.4f}")
    print(f"  Recall    : {base['recall']:.4f}")
    print(f"  F1-Score  : {base['f1_score']:.4f}")

    print(f"\n[Primary] {prim['model_name']} (v{prim.get('version', '1.0')}):")
    print(f"  Accuracy  : {prim['accuracy']*100:.2f}%")
    print(f"  Precision : {prim['precision']:.4f}")
    print(f"  Recall    : {prim['recall']:.4f}")
    print(f"  F1-Score  : {prim['f1_score']:.4f}")

    print("\nTop Contributing Features (Feature Importances):")
    for feat, imp in list(prim.get("top_feature_importances", {}).items())[:6]:
        print(f"  - {feat:30s}: {imp:.4f}")

    print("\n✅ Trained model saved to: data/models/delay_predictor.joblib")
    print("✅ Metrics saved to: data/models/evaluation_metrics.json")


if __name__ == "__main__":
    main()

