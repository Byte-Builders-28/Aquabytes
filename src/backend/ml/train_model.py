import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os


def load_real_dataset():
    path = "src/backend/ml/datasets/water_dataX.csv"
    df = pd.read_csv(path)

    # Rename columns to ML-friendly format
    df = df.rename(columns={
        "Temp": "temperature",
        "D.O. (mg/l)": "do",
        "PH": "ph",
        "CONDUCTIVITY (µmhos/cm)": "conductivity",
        "B.O.D. (mg/l)": "bod",
        "NITRATENAN N+ NITRITENANN (mg/l)": "nitrate",
        "FECAL COLIFORM (MPN/100ml)": "fecal_coliform",
        "TOTAL COLIFORM (MPN/100ml)Mean": "total_coliform",
    })

    # Replace NAN with median values
    df = df.replace("NAN", np.nan)
    df = df.astype({
        "temperature": float,
        "do": float,
        "ph": float,
        "conductivity": float,
        "bod": float,
        "nitrate": float,
        "fecal_coliform": float,
        "total_coliform": float
    })

    df = df.fillna(df.median(numeric_only=True))

    return df


def generate_labels(df):
    # Microbial Risk Label
    df["microbial_risk"] = df["fecal_coliform"].apply(
        lambda x: "Low" if x < 500 else
                  "Moderate" if x < 2500 else
                  "High" if x < 10000 else
                  "Critical"
    )

    # Heavy Metal Risk (proxy using conductivity + pH)
    df["heavy_metal_risk"] = df.apply(
        lambda row:
            "Critical" if row["conductivity"] > 1500 else
            "High" if row["conductivity"] > 800 else
            "Moderate" if row["ph"] < 6.5 or row["ph"] > 8.5 else
            "Low",
        axis=1
    )

    return df



def train_microbial_model(df):
    features = ["ph", "temperature", "do", "conductivity", "bod", "nitrate"]
    X = df[features]
    y = df["microbial_risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\nTraining Microbial Model...")
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=15,
        random_state=42,
        class_weight="balanced"
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("\nMicrobial Model Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))

    return model



def train_heavy_metal_model(df):
    features = ["ph", "temperature", "do", "conductivity", "bod"]
    X = df[features]
    y = df["heavy_metal_risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\nTraining Heavy Metal Model...")
    model = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=4
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("\nHeavy Metal Model Accuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))

    return model


def main():
    os.makedirs("src/backend/ml/models", exist_ok=True)

    print("Loading REAL dataset...")
    df = load_real_dataset()

    print("Generating labels from real measurements...")
    df = generate_labels(df)

    print("\nStarting training...")

    microbial_model = train_microbial_model(df)
    heavy_metal_model = train_heavy_metal_model(df)

    # Save models
    joblib.dump(microbial_model, "src/backend/ml/models/microbial_rf.joblib")
    joblib.dump(heavy_metal_model, "src/backend/ml/models/heavy_metal_rf.joblib")

    print("\nModels saved!")


if __name__ == "__main__":
    main()
