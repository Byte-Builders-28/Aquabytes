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

    def _estimate_coliform_presence(self, data: Dict[str, float]) -> str:
        """Estimate probability of coliform bacteria presence"""
        # This is a simplified heuristic model
        # Real detection requires lab culture tests
        
        if (data['do'] < 3 and data['turbidity'] > 15 and 
            data['temperature'] > 25):
            return "Very High (>70%)"
        elif (data['do'] < 5 and data['turbidity'] > 10):
            return "High (40-70%)"
        elif (data['do'] < 6 and data['turbidity'] > 5):
            return "Moderate (20-40%)"
        else:
            return "Low (<20%)"
    
    def predict_heavy_metal_risk(self, data: Dict[str, float]) -> Dict:
        """
        Estimate heavy metal contamination risk using proxy parameters
        
        Key Indicators:
        - High TDS → Dissolved metals
        - Low pH → Increased metal solubility
        - High conductivity (via TDS) → Ionic metals
        """
        risk_score = 0
        risk_factors = []
        
        # TDS Analysis (direct correlation with dissolved metals)
        if data['tds'] > 1500:
            risk_score += 35
            risk_factors.append("Very high TDS - significant dissolved metals likely")
        elif data['tds'] > 800:
            risk_score += 30
            risk_factors.append("High TDS - elevated metal concentration possible")
        elif data['tds'] > 500:
            risk_score += 15
            risk_factors.append("Moderate TDS - monitor for metals")
        
        # pH Analysis (acidic water dissolves more metals)
        if data['ph'] < 6.0:
            risk_score += 30
            risk_factors.append("Acidic water - high metal dissolution from pipes/soil")
        elif data['ph'] < 6.5:
            risk_score += 25
            risk_factors.append("Low pH - increased metal solubility")
        elif data['ph'] < 7.0:
            risk_score += 10
            risk_factors.append("Slightly acidic - potential metal leaching")
        
        # Conductivity proxy.... (TDS × 0.64 ≈ µS/cm)
        conductivity = data['tds'] * 0.64
        if conductivity > 1000:
            risk_score += 20
            risk_factors.append("Very high conductivity - ionic metals present")
        elif conductivity > 750:
            risk_score += 15
            risk_factors.append("High conductivity - potential ionic contamination")
        
        # Temperature effect on metal solubility
        if data['temperature'] > 30:
            risk_score += 5
            risk_factors.append("High temperature increases metal solubility")
        
       
        if data['ph'] < 6.5 and data['tds'] > 800:
            risk_score += 15
            risk_factors.append("Critical pH-TDS combination")
        
        if risk_score < 20:
            level = 'Low'
            recommendation = 'Likely safe, routine annual testing advised'
            action = 'Continue normal monitoring'
        elif risk_score < 40:
            level = 'Moderate'
            recommendation = 'Lab testing recommended within 3 months'
            action = 'Schedule ICP-MS/AAS lab test for Lead, Arsenic, Mercury, Cadmium'
        elif risk_score < 60:
            level = 'High'
            recommendation = 'Lab testing strongly recommended within 1 month'
            action = 'URGENT: Professional water quality testing required'
        else:
            level = 'Critical'
            recommendation = 'Immediate lab testing REQUIRED - avoid all consumption'
            action = 'STOP USAGE: Emergency testing for heavy metals necessary'
        
        return {
            'risk_score': min(risk_score, 100),
            'level': level,
            'recommendation': recommendation,
            'action_required': action,
            'risk_factors': risk_factors,
            'suspected_metals': self._identify_likely_metals(data)
        }

    def _identify_likely_metals(self, data: Dict[str, float]) -> List[str]:
        """Identify which heavy metals are most likely present
        If we want to do it precise ...test needed .."""
        
        suspects = []
        
        if data['ph'] < 6.5 and data['tds'] > 500:
            suspects.append("Lead (from pipes)")
            suspects.append("Copper (from plumbing)")
        
        if data['tds'] > 1000:
            suspects.append("Arsenic (geological)")
            suspects.append("Chromium")
        
        if data['ph'] < 6.0:
            suspects.append("Cadmium")
            suspects.append("Zinc")
        
        return suspects if suspects else ["No specific metals suspected"]

    def analyze_irrigation_suitability(self, data: Dict[str, float]) -> Dict:
        """
        Analyze water suitability for agricultural irrigation
        Based on FAO irrigation water quality guidelines
        """
        score = 100
        issues = []
        warnings = []
        
        # Salinity hazard (TDS/EC)
        if data['tds'] > 2000:
            score -= 40
            issues.append("Severe salinity hazard - NOT suitable for most crops")
            issues.append("Only extremely salt-tolerant crops may survive")
        elif data['tds'] > 1500:
            score -= 30
            issues.append("High salinity - suitable only for tolerant crops")
            warnings.append("Consider: Cotton, barley, sugar beet")
        elif data['tds'] > 1000:
            score -= 20
            issues.append("Moderate salinity - avoid sensitive crops")
            warnings.append("Avoid: Beans, strawberries, onions")
        elif data['tds'] > 450:
            score -= 10
            warnings.append("Slight salinity - monitor crop response")
        
        # pH suitability
        if data['ph'] < 5.5 or data['ph'] > 8.5:
            score -= 25
            issues.append(f"pH {data['ph']} outside acceptable range (5.5-8.5)")
            issues.append("May cause nutrient lockout and toxicity")
        elif data['ph'] < 6.0 or data['ph'] > 8.0:
            score -= 15
            warnings.append(f"pH {data['ph']} suboptimal - may need adjustment")
        
        # Turbidity (affects irrigation system)
        if data['turbidity'] > 50:
            score -= 20
            issues.append("Very high turbidity - will clog drip irrigation")
            warnings.append("Pre-filtration mandatory")
        elif data['turbidity'] > 20:
            score -= 10
            warnings.append("High turbidity - use sprinkler instead of drip")
        
        # Microbial risk check
        microbial = self.predict_microbial_risk(data)
        if microbial['risk_score'] > 60:
            score -= 25
            issues.append("High microbial contamination risk")
            warnings.append("Risk of crop pathogen transmission")
        elif microbial['risk_score'] > 40:
            score -= 15
            warnings.append("Moderate contamination - avoid edible crops")
        
        # DO   ...(important for hydroponics)
        if data['do'] < 4:
            warnings.append("Low DO - may stress plant roots in hydroponics")
        
        # Determine crop suitability
        suitable_crops = self._recommend_crops(data['tds'], data['ph'])
        
        return {
            'score': max(0, score),
            'suitable': score > 60,
            'rating': (
                'Excellent' if score > 85 else
                'Good' if score > 70 else
                'Fair' if score > 50 else
                'Poor' if score > 30 else
                'Unsuitable'
            ),
            'issues': issues if issues else ['Water suitable for irrigation'],
            'warnings': warnings,
            'suitable_crops': suitable_crops,
            'irrigation_method': self._recommend_irrigation_method(data)
        }
    
    def _recommend_crops(self, tds: float, ph: float) -> List[str]:
        """Recommend suitable crops based on water quality"""
        if tds < 450:
            return ['All crops', 'Fruits', 'Vegetables', 'Flowers']
        elif tds < 1000:
            return ['Tolerant vegetables', 'Cereals', 'Fodder crops']
        elif tds < 1500:
            return ['Barley', 'Cotton', 'Sugar beet', 'Date palm']
        elif tds < 2000:
            return ['Cotton', 'Barley (limited)']
        else:
            return ['Not recommended for agriculture']
    
    def _recommend_irrigation_method(self, data: Dict[str, float]) -> str:
        """Recommend best irrigation method based on water quality"""
        if data['turbidity'] > 50:
            return 'Flood/Surface irrigation (high turbidity)'
        elif data['turbidity'] > 20:
            return 'Sprinkler irrigation (moderate turbidity)'
        elif data['tds'] > 1500:
            return 'Drip with leaching (high salinity)'
        else:
            return 'Drip irrigation (optimal)'

    def generate_alerts(self, results: Dict) -> List[Dict]:
        """Generate actionable alerts based on analysis results"""
        alerts = []
        
        # WQI alerts
        if results['wqi']['wqi'] < 50:
            alerts.append({
                'type': 'water_quality',
                'severity': 'high',
                'message': f"Water Quality Index is {results['wqi']['category']} ({results['wqi']['wqi']})",
                'action': 'Investigate contamination source immediately'
            })
        
        # Microbial alerts
        if results['microbial_risk']['level'] in ['High', 'Critical']:
            alerts.append({
                'type': 'microbial',
                'severity': 'critical' if results['microbial_risk']['level'] == 'Critical' else 'high',
                'message': f"Microbial contamination risk: {results['microbial_risk']['level']}",
                'action': results['microbial_risk']['recommendation']
            })
        
        # Heavy metal alerts
        if results['heavy_metal_risk']['level'] in ['High', 'Critical']:
            alerts.append({
                'type': 'heavy_metal',
                'severity': 'critical' if results['heavy_metal_risk']['level'] == 'Critical' else 'high',
                'message': f"Heavy metal risk: {results['heavy_metal_risk']['level']}",
                'action': results['heavy_metal_risk']['action_required']
            })
        
        # Irrigation alerts
        if not results['irrigation_suitable']['suitable']:
            alerts.append({
                'type': 'irrigation',
                'severity': 'medium',
                'message': 'Water not suitable for irrigation',
                'action': 'Review crop selection and treatment options'
            })
        
        # Parameter-specific alerts
        sensor_data = results['sensor_data']
        if sensor_data['ph'] < 6.5 or sensor_data['ph'] > 8.5:
            alerts.append({
                'type': 'parameter',
                'severity': 'medium',
                'message': f"pH out of range: {sensor_data['ph']}",
                'action': 'Check for contamination or adjust pH if needed'
            })
        
        if sensor_data['tds'] > 1200:
            alerts.append({
                'type': 'parameter',
                'severity': 'medium',
                'message': f"High TDS: {sensor_data['tds']} ppm",
                'action': 'Consider water treatment or source replacement'
            })
        
        return alerts
    
    def analyze_water_sample(self, sensor_data: Dict[str, float]) -> Dict:
        """
        Complete water quality analysis pipeline
        Main entry point for all predictions
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'sensor_data': sensor_data,
            'wqi': self.calculate_wqi(sensor_data),
            'microbial_risk': self.predict_microbial_risk(sensor_data),
            'heavy_metal_risk': self.predict_heavy_metal_risk(sensor_data),
            'irrigation_suitable': self.analyze_irrigation_suitability(sensor_data)
        }
        
        # Add rooftop harvesting specific recommendations
        results['rooftop_harvest'] = self._analyze_rooftop_suitability(sensor_data, results)
        
        # Generate alerts
        results['alerts'] = self.generate_alerts(results)
        
        # Add recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _analyze_rooftop_suitability(self, data: Dict, full_results: Dict) -> Dict:
        """Analyze if rooftop harvested water is suitable for reuse"""
        purposes = {
            'drinking': False,
            'cooking': False,
            'washing': False,
            'irrigation': full_results['irrigation_suitable']['suitable'],
            'toilet_flushing': True
        }
        
        wqi = full_results['wqi']['wqi']
        microbial_risk = full_results['microbial_risk']['risk_score']
        
        # Drinking water standards (very strict)
        if wqi > 90 and microbial_risk < 20 and 6.5 <= data['ph'] <= 8.5 and data['tds'] < 500:
            purposes['drinking'] = True
            purposes['cooking'] = True
        
        # Washing/cleaning (moderate standards)
        if wqi > 70 and microbial_risk < 40:
            purposes['washing'] = True
        
        recommendations = []
        if not purposes['drinking']:
            recommendations.append("Install multi-stage filtration for potable use")
        if not purposes['cooking']:
            recommendations.append("Boil water before cooking use")
        if microbial_risk > 40:
            recommendations.append("UV sterilization recommended")
        if data['turbidity'] > 5:
            recommendations.append("Add sediment filter at first-flush stage")
        
        return {
            'suitable_purposes': purposes,
            'treatment_needed': not purposes['drinking'],
            'recommendations': recommendations,
            'estimated_quality': (
                'Potable after basic filtration' if wqi > 80 and microbial_risk < 30 else
                'Non-potable - treatment required' if wqi > 60 else
                'Poor quality - extensive treatment needed'
            )
        }
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if results['wqi']['wqi'] < 70:
            recommendations.append("Investigate and eliminate contamination sources")
        
        if results['microbial_risk']['risk_score'] > 40:
            recommendations.append("Install UV sterilization system")
            recommendations.append("Clean and disinfect storage tanks")
        
        if results['heavy_metal_risk']['risk_score'] > 40:
            recommendations.append("Test water samples in certified lab")
            recommendations.append("Consider reverse osmosis system")
        
        if results['sensor_data']['turbidity'] > 10:
            recommendations.append("Install multi-stage filtration (sediment + activated carbon)")
        
        if results['sensor_data']['tds'] > 1000:
            recommendations.append("Check for groundwater contamination or pipe corrosion")
        
        return recommendations