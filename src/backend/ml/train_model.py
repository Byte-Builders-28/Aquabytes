"""
Script to train ML models on water quality datasets
This is optional - the system works with rule-based models too
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

def generate_synthetic_training_data(n_samples=10000):

    np.random.seed(42)
    
    data = {
        'ph': np.random.normal(7.0, 1.5, n_samples).clip(4, 10),
        'tds': np.random.lognormal(6.0, 0.8, n_samples).clip(50, 3000),
        'turbidity': np.random.lognormal(1.5, 1.2, n_samples).clip(0.1, 100),
        'temperature': np.random.normal(25, 5, n_samples).clip(10, 40),
        'do': np.random.normal(7, 2, n_samples).clip(0, 14)
    }
    
    df = pd.DataFrame(data)
    
    # Generate labels for microbial contamination
    # Based on correlated risk factors
    df['microbial_risk'] = (
        ((df['do'] < 4) * 30) +
        ((df['turbidity'] > 10) * 25) +
        ((df['temperature'] > 30) * 20) +
        ((df['ph'] < 6.5) | (df['ph'] > 8.5)) * 15 +
        ((df['tds'] > 1000) * 10)
    )
    df['microbial_risk'] = df['microbial_risk'].apply(
        lambda x: 'Low' if x < 20 else 'Moderate' if x < 40 else 'High' if x < 60 else 'Critical'
    )
    
    # Generate labels for heavy metal risk
    df['heavy_metal_risk'] = (
        ((df['tds'] > 800) * 30) +
        ((df['ph'] < 6.5) * 25) +
        ((df['tds'] * 0.64 > 750) * 20)
    )
    df['heavy_metal_risk'] = df['heavy_metal_risk'].apply(
        lambda x: 'Low' if x < 20 else 'Moderate' if x < 40 else 'High' if x < 60 else 'Critical'
    )
    
    return df

def train_microbial_model():
    """Train Random Forest for microbial contamination prediction"""
    print("Generating synthetic training data...")
    df = generate_synthetic_training_data()
    
    features = ['ph', 'tds', 'turbidity', 'temperature', 'do']
    X = df[features]
    y = df['microbial_risk']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("\nTraining Microbial Risk Model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    print("\nMicrobial Model Performance:")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Feature importance
    importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print("\nFeature Importance:")
    print(importance)
    
    return model

def train_heavy_metal_model():
    """Train model for heavy metal risk prediction"""
    print("\n" + "="*50)
    print("Training Heavy Metal Risk Model...")
    df = generate_synthetic_training_data()
    
    features = ['ph', 'tds', 'turbidity', 'temperature', 'do']
    X = df[features]
    y = df['heavy_metal_risk']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    model = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    print("\nHeavy Metal Model Performance:")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    return model

def main():
    """Train and save all models"""
    # Create models directory
    os.makedirs('src/backend/ml/models', exist_ok=True)
    
    # Train models
    microbial_model = train_microbial_model()
    heavy_metal_model = train_heavy_metal_model()
    
    # Save models
    print("\n" + "="*50)
    print("Saving models...")
    joblib.dump(microbial_model, 'src/backend/ml/models/microbial_rf.joblib')
    joblib.dump(heavy_metal_model, 'src/backend/ml/models/heavy_metal_rf.joblib')
    
    print("\nModels saved successfully!")
    print("- backend/app/ml/models/microbial_rf.joblib")
    print("- backend/app/ml/models/heavy_metal_rf.joblib")

if __name__ == "__main__":
    main()
