import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os


def load_real_dataset():
    """
    Load the real water quality dataset from CSV
    """
    print("Loading water quality dataset from CSV...")
    
    # Try different paths and encodings
    possible_paths = [
        "water_dataX.csv",
        "src/backend/ml/datasets/water_dataX.csv",
        "../../../water_dataX.csv",
        "../../water_dataX.csv"
    ]
    
    df = None
    loaded_path = None
    
    for path in possible_paths:
        if not os.path.exists(path):
            continue
            
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
            try:
                df = pd.read_csv(path, encoding=encoding)
                loaded_path = path
                print(f"✓ Loaded {len(df)} records from {path} (encoding: {encoding})")
                break
            except (UnicodeDecodeError, FileNotFoundError):
                continue
        
        if df is not None:
            break
    
    if df is None:
        print("ERROR: water_dataX.csv not found or could not be read!")
        print("Searched in:")
        for path in possible_paths:
            print(f"  - {path}")
        print("\nPlease make sure the CSV file is accessible.")
        exit(1)
    
    # Print column names to see what we have
    print("\nAvailable columns in CSV:")
    print(df.columns.tolist())
    
    # Map CSV columns to our model parameters
    # CSV has: Temp, D.O. (mg/l), PH, CONDUCTIVITY (µmhos/cm), B.O.D. (mg/l), 
    #          NITRATENAN N+ NITRITENANN (mg/l), FECAL COLIFORM, TOTAL COLIFORM
    
    column_mapping = {
        'Temp': 'temperature',
        'D.O. (mg/l)': 'do',
        'PH': 'ph',
        'CONDUCTIVITY (µmhos/cm)': 'conductivity',
        'B.O.D. (mg/l)': 'bod',
        'NITRATENAN N+ NITRITENANN (mg/l)': 'nitrate',
        'FECAL COLIFORM (MPN/100ml)': 'fecal_coliform',
        'TOTAL COLIFORM (MPN/100ml)Mean': 'total_coliform'
    }
    
    # Rename columns
    df = df.rename(columns=column_mapping)
    
    # Print renamed columns to verify
    print("\nRenamed columns:")
    print(df.columns.tolist())
    
    # Select only the columns we need (only if they exist after renaming)
    needed_columns = ['temperature', 'do', 'ph', 'conductivity', 'bod', 'nitrate', 'fecal_coliform', 'total_coliform']
    
    # Check which columns are actually present
    available_needed = [col for col in needed_columns if col in df.columns]
    missing_columns = [col for col in needed_columns if col not in df.columns]
    
    if missing_columns:
        print(f"\nWARNING: Missing columns: {missing_columns}")
        print("Will use only available columns...")
    
    df = df[available_needed]
    
    # Handle missing values (NAN strings and actual NaN)
    print("\nHandling missing values...")
    
    # Replace 'NAN' strings with NaN
    df = df.replace('NAN', np.nan)
    df = df.replace('nan', np.nan)
    
    # Convert all columns to numeric, forcing errors to NaN
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    print(f"Missing values before cleaning:\n{df.isnull().sum()}")
    
    # Fill missing values with column mean for numerical stability
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            df[col].fillna(df[col].mean(), inplace=True)
    
    # For any remaining NaN (if mean was NaN), fill with reasonable defaults
    defaults = {
        'temperature': 25.0,
        'do': 7.0,
        'ph': 7.0,
        'conductivity': 500.0,
        'bod': 2.0,
        'nitrate': 0.5,
        'fecal_coliform': 100.0,
        'total_coliform': 200.0
    }
    
    for col, default_val in defaults.items():
        if df[col].isnull().sum() > 0:
            df[col].fillna(default_val, inplace=True)
    
    print(f"Missing values after cleaning:\n{df.isnull().sum()}")
    
    # Add turbidity as a synthetic parameter (not in CSV)
    # We can estimate it from other parameters or use random values
    print("\nGenerating synthetic turbidity values (not in CSV)...")
    np.random.seed(42)
    
    # Turbidity tends to correlate with BOD and total coliform
    # Higher BOD and coliform = higher turbidity
    df['turbidity'] = (
        np.random.lognormal(1.5, 1.0, len(df)).clip(0.1, 100) * 
        (1 + df['bod'] / 10) * 
        (1 + np.log10(df['total_coliform'] + 1) / 5)
    ).clip(0.1, 100)
    
    # Add TDS (Total Dissolved Solids) as a synthetic parameter
    # TDS correlates with conductivity: TDS (ppm) ≈ Conductivity (µS/cm) * 0.64
    print("Generating TDS from conductivity...")
    df['tds'] = (df['conductivity'] * 0.64).clip(10, 3000)
    
    print(f"\n✓ Final dataset shape: {df.shape}")
    print(f"✓ Total records: {len(df)}")
    print("\nDataset statistics:")
    print(df.describe())
    
    return df


def generate_labels(df):
    """
    Generate risk labels from real measurements
    """
    print("\nGenerating risk labels from measurements...")
    
    # Microbial Risk Label (based on fecal coliform - WHO standards)
    # WHO guidelines: <10 MPN/100ml (excellent), <100 (good), <1000 (fair), >1000 (poor)
    df["microbial_risk"] = df["fecal_coliform"].apply(
        lambda x: "Low" if x < 100 else
                  "Moderate" if x < 1000 else
                  "High" if x < 10000 else
                  "Critical"
    )
    
    print(f"Microbial risk distribution:\n{df['microbial_risk'].value_counts()}")
    
    # Heavy Metal Risk (proxy using conductivity + pH + TDS)
    # High conductivity/TDS + extreme pH = higher heavy metal risk
    def calculate_heavy_metal_risk(row):
        risk_score = 0
        
        # High TDS/conductivity indicates dissolved metals
        if row["tds"] > 1500 or row["conductivity"] > 2000:
            risk_score += 35
        elif row["tds"] > 800 or row["conductivity"] > 1200:
            risk_score += 25
        elif row["tds"] > 500 or row["conductivity"] > 800:
            risk_score += 15
        
        # Acidic pH dissolves more metals
        if row["ph"] < 6.0:
            risk_score += 30
        elif row["ph"] < 6.5:
            risk_score += 20
        elif row["ph"] > 8.5:
            risk_score += 10
        
        # Low DO can indicate contamination
        if row["do"] < 4:
            risk_score += 10
        
        if risk_score < 20:
            return "Low"
        elif risk_score < 40:
            return "Moderate"
        elif risk_score < 60:
            return "High"
        else:
            return "Critical"
    
    df["heavy_metal_risk"] = df.apply(calculate_heavy_metal_risk, axis=1)
    
    print(f"Heavy metal risk distribution:\n{df['heavy_metal_risk'].value_counts()}")
    
    return df


def train_microbial_model(df):
    """
    Train Random Forest model for microbial contamination prediction
    """
    features = ["ph", "temperature", "do", "conductivity", "bod", "nitrate", "turbidity"]
    X = df[features]
    y = df["microbial_risk"]
    
    # Check for any remaining NaN
    if X.isnull().sum().sum() > 0:
        print("WARNING: Found NaN values in features, filling with mean...")
        X = X.fillna(X.mean())
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("\n" + "="*60)
    print("Training Microbial Risk Model...")
    print("="*60)
    
    model = RandomForestClassifier(
        n_estimators=150,
        max_depth=15,
        min_samples_split=10,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1  # Use all CPU cores
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✓ Microbial Model Accuracy: {accuracy:.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Feature importance
    importance_df = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature Importance:")
    print(importance_df)
    print(1)
    return model
    print(2)

def train_heavy_metal_model(df):
    """
    Train Gradient Boosting model for heavy metal risk prediction
    """
    features = ["ph", "temperature", "do", "conductivity", "bod", "tds"]
    X = df[features]
    y = df["heavy_metal_risk"]
    
    # Check for any remaining NaN
    if X.isnull().sum().sum() > 0:
        print("WARNING: Found NaN values in features, filling with mean...")
        X = X.fillna(X.mean())
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("\n" + "="*60)
    print("Training Heavy Metal Risk Model...")
    print("="*60)
    
    model = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=4,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✓ Heavy Metal Model Accuracy: {accuracy:.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Feature importance
    importance_df = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature Importance:")
    print(importance_df)
    
    return model


def main():
    """
    Main training pipeline
    """
    print("="*60)
    print("Water Quality ML Model Training")
    print("="*60)
    
    # Create models directory
    os.makedirs("src/backend/ml/models", exist_ok=True)
    
    # Load real dataset
    df = load_real_dataset()
    
    # Generate labels from real measurements
    df = generate_labels(df)
    
    # Train models
    microbial_model = train_microbial_model(df)
    heavy_metal_model = train_heavy_metal_model(df)
    
    # Save models
    print("\n" + "="*60)
    print("Saving trained models...")
    print("="*60)
    
    joblib.dump(microbial_model, "src/backend/ml/models/microbial_rf.joblib")
    print("✓ Saved: src/backend/ml/models/microbial_rf.joblib")
    
    joblib.dump(heavy_metal_model, "src/backend/ml/models/heavy_metal_rf.joblib")
    print("✓ Saved: src/backend/ml/models/heavy_metal_rf.joblib")
    
    print("\n" + "="*60)
    print("✓ Training completed successfully!")
    print("="*60)
    print("\nYou can now use these models in your FastAPI backend.")
    print("The models will automatically load when you start the server.")


if __name__ == "__main__":
    main()