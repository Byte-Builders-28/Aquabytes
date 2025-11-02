import joblib
from ml.preprocess import preprocess_input

model_path = "src/backend/ml/model.pkl"
model = joblib.load(model_path)

def predict_quality(sensor_data: dict):
    """
    Predicts contamination or water quality category based on sensor data.
    """
    df = preprocess_input(sensor_data)
    prediction = model.predict(df)[0]

    if hasattr(model, "predict_proba"):
        confidence = model.predict_proba(df).max()
    else:
        confidence = None

    return {"prediction": str(prediction), "confidence": confidence}

