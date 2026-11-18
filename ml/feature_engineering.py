"""
ml/feature_engineering.py
=========================
Feature Engineering Pipeline for Logistics Delay Prediction.

CRITICAL: PREVENTS TARGET LEAKAGE
    We strictly EXCLUDE features that are only known AFTER a shipment completes:
    - actual_pickup
    - actual_delivery
    - delay_minutes
    - delay_reason
    - status

    We ONLY use features known at order creation or dispatch planning time:
    - origin_city, destination_city
    - distance_km
    - weight_kg
    - vehicle_type
    - carrier
    - category
    - scheduled_hour (hour of day)
    - scheduled_day_of_week (day of week: 0=Mon, 6=Sun)
    - scheduled_month (seasonality)
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Tuple, List

# Canonical numeric and categorical feature sets
NUMERIC_FEATURES = [
    "distance_km",
    "weight_kg",
    "scheduled_hour",
    "scheduled_day_of_week",
    "scheduled_month",
]

CATEGORICAL_FEATURES = [
    "vehicle_type",
    "carrier",
    "category",
    "origin_city",
    "destination_city",
]

ALL_FEATURE_COLS = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def extract_datetime_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract temporal features from scheduled_pickup datetime."""
    df_out = df.copy()

    if "scheduled_pickup" in df_out.columns:
        dt_series = pd.to_datetime(df_out["scheduled_pickup"], errors="coerce")
        df_out["scheduled_hour"] = dt_series.dt.hour.fillna(10).astype(int)
        df_out["scheduled_day_of_week"] = getattr(dt_series.dt, "day_of_week", dt_series.dt.dayofweek).fillna(2).astype(int)
        df_out["scheduled_month"] = dt_series.dt.month.fillna(6).astype(int)
    else:
        # Fallback if raw timestamp column is missing
        if "scheduled_hour" not in df_out.columns:
            df_out["scheduled_hour"] = 10
        if "scheduled_day_of_week" not in df_out.columns:
            df_out["scheduled_day_of_week"] = 2
        if "scheduled_month" not in df_out.columns:
            df_out["scheduled_month"] = 6

    return df_out


def prepare_features_and_target(
    df: pd.DataFrame,
    target_col: str = "is_delayed",
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Filter, clean, and extract features and target variable from input DataFrame.

    Returns:
        X (pd.DataFrame with ALL_FEATURE_COLS), y (pd.Series)
    """
    df_clean = extract_datetime_features(df)

    # Impute missing numeric columns with median
    for col in NUMERIC_FEATURES:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce").fillna(0.0)
        else:
            df_clean[col] = 0.0

    # Impute missing categorical columns with 'Unknown'
    for col in CATEGORICAL_FEATURES:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.strip().fillna("Unknown")
        else:
            df_clean[col] = "Unknown"

    X = df_clean[ALL_FEATURE_COLS].copy()

    if target_col in df_clean.columns:
        y = pd.to_numeric(df_clean[target_col], errors="coerce").fillna(0).astype(int)
    else:
        y = pd.Series(0, index=df_clean.index)

    return X, y

