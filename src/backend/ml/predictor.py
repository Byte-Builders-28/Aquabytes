import numpy as np
from typing import Dict, List
from datetime import datetime
import joblib
import os

class WaterQualityPredictor:
    def __init__(self):
        # WHO/BIS/EPA standard thresholds.... I get this after reading various boring journals fro WHO,BIS,epa
        self.standards = {
            'ph': {'min': 6.5, 'max': 8.5, 'ideal': 7.0},
            'tds': {'excellent': 300, 'good': 600, 'fair': 900, 'poor': 1200},
            'turbidity': {'excellent': 1, 'good': 5, 'fair': 10, 'poor': 25},
            'do': {'excellent': 6, 'good': 4, 'fair': 2},
            'temperature': {'min': 0, 'max': 40, 'ideal': 25}
        }
        

        self.ml_models = self._load_ml_models()
    
    def _load_ml_models(self):
        """Load trained ML models (Random Forest, OR what suits more....) TEST IN PROGRESS ..."""
        models = {}
        model_path = 'backend/app/ml/models/'
        
        try:
            if os.path.exists(f'{model_path}microbial_rf.joblib'):
                models['microbial'] = joblib.load(f'{model_path}microbial_rf.joblib')
            if os.path.exists(f'{model_path}heavy_metal_rf.joblib'):
                models['heavy_metal'] = joblib.load(f'{model_path}heavy_metal_rf.joblib')
        except Exception as e:
            print(f"Models not found, using rule-based system: {e}")
        
        return models
    
    def calculate_wqi(self, data: Dict[str, float]) -> Dict:
       
        # pH sub-index (deviation from ideal)
        ph_deviation = abs(data['ph'] - self.standards['ph']['ideal']) / self.standards['ph']['ideal']
        ph_score = max(0, 100 - (ph_deviation * 100))
        
        # TDS sub-index
        tds = data['tds']
        if tds < 300:
            tds_score = 100
        elif tds < 600:
            tds_score = 80
        elif tds < 900:
            tds_score = 60
        elif tds < 1200:
            tds_score = 40
        else:
            tds_score = 20
        
        # Turbidity sub-index
        turb = data['turbidity']
        if turb < 1:
            turb_score = 100
        elif turb < 5:
            turb_score = 80
        elif turb < 10:
            turb_score = 60
        elif turb < 25:
            turb_score = 40
        else:
            turb_score = 20
        
        # DO sub-index
        do = data['do']
        if do > 6:
            do_score = 100
        elif do > 4:
            do_score = 70
        elif do > 2:
            do_score = 40
        else:
            do_score = 20
        
        # Temperature sub-index (affects biological activity)... just boring biologies
        temp = data['temperature']
        if 20 <= temp <= 30:
            temp_score = 100
        elif 15 <= temp <= 35:
            temp_score = 80
        else:
            temp_score = 60
        
        #  WQI calculation as weights (can be changed as needs)....
        
        wqi = (
            ph_score * 0.25 +
            tds_score * 0.30 +
            turb_score * 0.25 +
            do_score * 0.15 +
            temp_score * 0.05
        )
        
        # Categorize WQI
        if wqi > 90:
            category = 'Excellent'
        elif wqi > 70:
            category = 'Good'
        elif wqi > 50:
            category = 'Fair'
        elif wqi > 25:
            category = 'Poor'
        else:
            category = 'Very Poor'
        
        return {
            'wqi': round(wqi, 2),
            'category': category,
            'sub_indices': {
                'ph': round(ph_score, 2),
                'tds': round(tds_score, 2),
                'turbidity': round(turb_score, 2),
                'do': round(do_score, 2),
                'temperature': round(temp_score, 2)
            }
        }

         def predict_microbial_risk(self, data: Dict[str, float]) -> Dict:
        """
        Predict microbial contamination risk using proxy parameters
        A backup plan for now to get rid of stupid lab douradori
        Logic as per my AIIMS friend :
        - Low DO → Organic matter decomposition (bacterial activity)
        - High Turbidity → Suspended particles (bacterial carriers)
        - High Temperature → Bacterial growth acceleration
        - pH extremes → Stress indicators
        - High TDS → Potential contamination
        """
        risk_score = 0
        risk_factors = []
        
        # D0 analysis
        if data['do'] < 2:
            risk_score += 35
            risk_factors.append("Critical DO level - severe organic contamination")
        elif data['do'] < 4:
            risk_score += 30
            risk_factors.append("Low DO - organic matter decomposition")
        elif data['do'] < 6:
            risk_score += 15
            risk_factors.append("Moderate DO - monitor for contamination")
        
        # Turbidity 
        if data['turbidity'] > 25:
            risk_score += 30
            risk_factors.append("Very high turbidity - high bacterial carrier potential")
        elif data['turbidity'] > 10:
            risk_score += 25
            risk_factors.append("High turbidity - suspended particles present")
        elif data['turbidity'] > 5:
            risk_score += 15
            risk_factors.append("Elevated turbidity - filtration recommended")
        
        # Temperature Analysis 
        # (bacterial growth optimal 25-37°C) - I have to ask my AIIMS freind to get this  
        if data['temperature'] > 35:
            risk_score += 25
            risk_factors.append("High temperature - accelerated bacterial growth")
        elif data['temperature'] > 30:
            risk_score += 20
            risk_factors.append("Warm water - favorable for bacteria")
        elif data['temperature'] > 25:
            risk_score += 10
            risk_factors.append("Moderate temperature - routine monitoring needed")
        
        # pH
        if data['ph'] < 6.0 or data['ph'] > 9.0:
            risk_score += 20
            risk_factors.append("Extreme pH - stress indicator")
        elif data['ph'] < 6.5 or data['ph'] > 8.5:
            risk_score += 15
            risk_factors.append("pH outside ideal range")
        
        # TDS 
        if data['tds'] > 1500:
            risk_score += 15
            risk_factors.append("Very high TDS - contamination likely")
        elif data['tds'] > 1000:
            risk_score += 10
            risk_factors.append("High TDS - increased contamination risk")
        
        # synergistic effects
        if data['do'] < 4 and data['turbidity'] > 10:
            risk_score += 10
            risk_factors.append("Combined DO and turbidity risk")
        
        if data['temperature'] > 30 and data['do'] < 6:
            risk_score += 10
            risk_factors.append("Temperature-DO combination increases risk")
        
        # risk lvls
        if risk_score < 20:
            level = 'Low'
            recommendation = 'Safe for irrigation and non-potable uses'
        elif risk_score < 40:
            level = 'Moderate'
            recommendation = 'Monitor closely, consider basic filtration for sensitive uses'
        elif risk_score < 60:
            level = 'High'
            recommendation = 'Filtration and treatment required before any use'
        else:
            level = 'Critical'
            recommendation = 'DO NOT USE - Immediate treatment and lab testing required'
        
        return {
            'risk_score': min(risk_score, 100),
            'level': level,
            'recommendation': recommendation,
            'risk_factors': risk_factors,
            'coliform_probability': self._estimate_coliform_presence(data)
        }

