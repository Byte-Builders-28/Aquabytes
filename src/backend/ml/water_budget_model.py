# water_budget_model.py
import pickle
import numpy as np
import os

MODEL_PATH = "backend/ml/models/water_risk_model.pkl"

# Load model at import
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError("Train the model first using train.py!")

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

def predict_water_risk(tank_cap, current_level, dwellers, avg_need, rain_next7_list, dry_days, ph=None, tds=None):
    """
    Predict water risk using trained DecisionTree model + optional water quality.
    Keeps original tips/suggestion for storage, adds quality risk separately.
    """
    rain_next7 = sum(rain_next7_list) / len(rain_next7_list) if rain_next7_list else 0.0

    # Original storage-based risk
    X = np.array([[tank_cap, current_level, dwellers, avg_need, rain_next7, dry_days]])
    storage_risk = model.predict(X)[0]

    if storage_risk == 1:
        storage_suggestion = "Risk: Low storage + less rainfall ahead. Save water urgently!"
        storage_tips = [
            "Use buckets instead of showers",
            "Avoid washing vehicles",
            "Recycle greywater for gardening",
            "Prioritize drinking and cooking needs",
            "Cover tanks to reduce evaporation"
        ]
    else:
        storage_suggestion = "Safe: Tank level and rainfall forecast are sufficient."
        storage_tips = [
            "Maintain moderate use",
            "Harvest extra rain if possible",
            "Increase groundwater recharge (RTRWH/AR)",
            "Monitor weekly usage",
            "Clean rooftop filters regularly"
        ]

    # Water quality risk
    quality_risk = 0
    quality_msg = "Water quality is within safe limits."
    if ph is not None and (ph < 6.5 or ph > 8.5):
        quality_risk = 1
        quality_msg = "Unsafe pH levels! Water may be acidic or alkaline."
    elif tds is not None and tds > 500:
        quality_risk = 1
        quality_msg = "High TDS detected. Water is not potable."

    # Overall suggestion
    overall_risk = max(storage_risk, quality_risk)
    if overall_risk == 1:
        overall_suggestion = "⚠️ High Risk: Storage or quality issues detected!"
    else:
        overall_suggestion = "✅ Safe: Storage and water quality are acceptable."

    return {
        "ph" : ph,
        "tds": tds,
        "storage_risk": int(storage_risk),
        "storage_suggestion": storage_suggestion,
        "storage_tips": storage_tips,
        "quality_risk": int(quality_risk),
        "quality_message": quality_msg,
        "overall_suggestion": overall_suggestion,
        "rain_forecast": rain_next7_list
    }
