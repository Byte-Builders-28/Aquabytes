import numpy as np
import pandas as pd

def preprocess_input(data: dict):

    
    expected_features = ["pH", "tds", "turbidity", "temperature", "dissolved_oxygen"]
    
    for feature in expected_features:
        data.setdefault(feature, 0)

    df = pd.DataFrame([data])
    return df