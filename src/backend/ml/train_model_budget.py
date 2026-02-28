import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import pickle
import os

DATA_PATH = "../../../../data_engineering/data/synthetic_training.csv"
MODEL_DIR = "ML_models"
MODEL_PATH = os.path.join(MODEL_DIR, "water_risk_model.pkl")

def train_and_save_model():
    # Load dataset
    df = pd.read_csv(DATA_PATH)

    X = df[["TankCap","CurrentLevel","Dwellers","AvgNeed","RainNext7","DryDays"]]
        # If 'label' column doesn't exist, create it using a rule
    if "label" not in df.columns:
        df["label"] = df.apply(lambda row: 1 if (
            row["CurrentLevel"] < 0.3 * row["TankCap"] and row["RainNext7"] < 20
        ) else 0, axis=1)

    y = df["label"]
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    clf = DecisionTreeClassifier(max_depth=5, random_state=42)
    clf.fit(X_train, y_train)

    # Ensure model dir exists
    os.makedirs(MODEL_DIR, exist_ok=True)

    # Save trained model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)

    print(f"✅ Model trained and saved at {MODEL_PATH}")

if __name__ == "__main__":
    train_and_save_model()



