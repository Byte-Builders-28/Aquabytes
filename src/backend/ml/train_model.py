import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load dataset later dowbloaded from a reliable source (kaggle)
data = pd.read_csv("water_quality.csv")

X = data[["pH", "tds", "turbidity", "temperature", "dissolved_oxygen"]]
y = data["label"] 

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

joblib.dump(model, "src/backend/ml/model.pkl")
