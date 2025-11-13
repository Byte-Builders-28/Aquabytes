from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import datetime
import uvicorn

# Import predictor (make sure ml/predictor.py exists in same structure)
from ml.predictor import WaterQualityPredictor

app = FastAPI(
    title="Water Quality ML API",
    version="1.0.0",
    description="Real-time water quality analysis using ML models (No Database)"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML predictor
predictor = WaterQualityPredictor()

# In-memory storage (temporary, resets on restart)
readings_storage = []
alerts_storage = []

# Pydantic models
class SensorData(BaseModel):
    ph: float = Field(..., ge=0, le=14, description="pH value (0-14)")
    tds: float = Field(..., ge=0, description="Total Dissolved Solids in ppm")
    turbidity: float = Field(..., ge=0, description="Turbidity in NTU")
    temperature: float = Field(..., ge=-10, le=60, description="Temperature in Celsius")
    do: float = Field(..., ge=0, le=20, description="Dissolved Oxygen in mg/L")
    location: Optional[str] = None
    device_id: Optional[str] = "unknown"

    class Config:
        json_schema_extra = {
            "example": {
                "ph": 7.2,
                "tds": 350,
                "turbidity": 2.5,
                "temperature": 25,
                "do": 7.5,
                "location": "Rooftop Tank 1",
                "device_id": "ESP32_001"
            }
        }

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "Water Quality ML Backend API (No Database)",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "predict": "/api/v1/predict",
            "history": "/api/v1/history",
            "alerts": "/api/v1/alerts/{device_id}",
            "health": "/health",
            "docs": "/docs"
        },
        "note": "Data stored in memory only - resets on restart"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model": "loaded",
        "timestamp": datetime.now().isoformat(),
        "total_readings": len(readings_storage),
        "total_alerts": len(alerts_storage)
    }

@app.post("/api/v1/predict")
async def predict_water_quality(data: SensorData):
    """
    Analyze water quality from sensor data
    
    This endpoint takes sensor readings and returns comprehensive water quality analysis including:
    - Water Quality Index (WQI)
    - Microbial contamination risk
    - Heavy metal contamination risk
    - Irrigation suitability
    - Rooftop harvest recommendations
    - Actionable alerts
    """
    try:
        # Convert Pydantic model to dict
        sensor_dict = {
            'ph': data.ph,
            'tds': data.tds,
            'turbidity': data.turbidity,
            'temperature': data.temperature,
            'do': data.do
        }
        
        # Run ML prediction
        results = predictor.analyze_water_sample(sensor_dict)
        
        # Add metadata to results
        results['location'] = data.location
        results['device_id'] = data.device_id
        
        # Store in memory with ID
        reading_id = len(readings_storage) + 1
        results['reading_id'] = reading_id
        
        reading_entry = {
            'id': reading_id,
            'timestamp': results['timestamp'],
            'device_id': data.device_id,
            'location': data.location,
            'sensor_data': sensor_dict,
            'prediction': {
                'wqi': results['wqi']['wqi'],
                'wqi_category': results['wqi']['category'],
                'microbial_risk_level': results['microbial_risk']['level'],
                'heavy_metal_risk_level': results['heavy_metal_risk']['level'],
                'irrigation_suitable': results['irrigation_suitable']['suitable']
            }
        }
        readings_storage.append(reading_entry)
        
        # Store critical alerts in memory
        for alert in results['alerts']:
            if alert['severity'] in ['high', 'critical']:
                alert_entry = {
                    'id': len(alerts_storage) + 1,
                    'device_id': data.device_id,
                    'alert_type': alert['type'],
                    'severity': alert['severity'],
                    'message': alert['message'],
                    'created_at': datetime.now().isoformat(),
                    'is_resolved': False
                }
                alerts_storage.append(alert_entry)
        
        return {
            "success": True,
            "message": "Water quality analysis completed",
            "data": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/api/v1/history")
async def get_historical_data(
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    limit: int = Query(default=100, le=1000, description="Maximum number of records to return")
):
    """
    Retrieve historical sensor readings and predictions (from memory)
    """
    try:
        # Filter by device_id if provided
        filtered_readings = readings_storage
        if device_id:
            filtered_readings = [r for r in readings_storage if r['device_id'] == device_id]
        
        # Get latest readings (reverse order)
        history = list(reversed(filtered_readings))[:limit]
        
        return {
            "success": True,
            "count": len(history),
            "total_stored": len(readings_storage),
            "data": history,
            "note": "Data stored in memory only - will be lost on restart"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

@app.get("/api/v1/alerts/{device_id}")
async def get_device_alerts(device_id: str, resolved: bool = False):
    """
    Get alerts for a specific device
    """
    try:
        filtered_alerts = [
            a for a in alerts_storage 
            if a['device_id'] == device_id and (resolved or not a['is_resolved'])
        ]
        
        # Sort by created_at descending
        filtered_alerts.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            "success": True,
            "device_id": device_id,
            "count": len(filtered_alerts),
            "alerts": filtered_alerts[:50]  # Limit to 50 most recent
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert retrieval error: {str(e)}")

@app.put("/api/v1/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int):
    """
    Mark an alert as resolved
    """
    try:
        alert = next((a for a in alerts_storage if a['id'] == alert_id), None)
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert['is_resolved'] = True
        alert['resolved_at'] = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": "Alert resolved",
            "alert_id": alert_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resolution error: {str(e)}")

@app.get("/api/v1/dashboard/{device_id}")
async def get_dashboard_data(device_id: str):
    """
    Get comprehensive dashboard data for a device
    """
    try:
        # Get device readings
        device_readings = [r for r in readings_storage if r['device_id'] == device_id]
        
        if not device_readings:
            raise HTTPException(
                status_code=404, 
                detail=f"No data found for device: {device_id}"
            )
        
        # Latest reading
        latest = device_readings[-1]
        
        # Active alerts
        active_alerts = [
            a for a in alerts_storage 
            if a['device_id'] == device_id and not a['is_resolved']
        ]
        
        # Calculate simple trends (last 10 readings)
        recent = device_readings[-10:] if len(device_readings) >= 10 else device_readings
        trends = calculate_trends(recent)
        
        return {
            "success": True,
            "device_id": device_id,
            "latest_reading": {
                "timestamp": latest['timestamp'],
                **latest['sensor_data']
            },
            "prediction": latest['prediction'],
            "trends": trends,
            "active_alerts": [
                {
                    "type": a['alert_type'],
                    "severity": a['severity'],
                    "message": a['message'],
                    "created_at": a['created_at']
                }
                for a in active_alerts
            ],
            "total_readings": len(device_readings)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")

def calculate_trends(readings: List[Dict]) -> Dict:
    """Calculate parameter trends from recent readings"""
    if len(readings) < 2:
        return {"status": "insufficient_data"}
    
    # Split into two halves
    mid = len(readings) // 2
    first_half = readings[:mid]
    second_half = readings[mid:]
    
    def avg(items, param):
        values = [item['sensor_data'][param] for item in items]
        return sum(values) / len(values) if values else 0
    
    trends = {}
    for param in ['ph', 'tds', 'turbidity', 'temperature', 'do']:
        avg_first = avg(first_half, param)
        avg_second = avg(second_half, param)
        
        if avg_first > 0:
            change_pct = ((avg_second - avg_first) / avg_first) * 100
            trends[param] = {
                "direction": "increasing" if change_pct > 5 else "decreasing" if change_pct < -5 else "stable",
                "change_percent": round(change_pct, 2)
            }
    
    return trends

@app.get("/api/v1/stats/summary")
async def get_system_summary():
    """
    Get overall system statistics
    """
    try:
        total_readings = len(readings_storage)
        unique_devices = len(set(r['device_id'] for r in readings_storage))
        active_alerts = sum(1 for a in alerts_storage if not a['is_resolved'])
        
        # Calculate average WQI from recent predictions
        if readings_storage:
            recent_wqis = [r['prediction']['wqi'] for r in readings_storage[-100:]]
            avg_wqi = sum(recent_wqis) / len(recent_wqis) if recent_wqis else 0
            
            # Count WQI categories
            wqi_categories = {}
            for r in readings_storage[-100:]:
                category = r['prediction']['wqi_category']
                wqi_categories[category] = wqi_categories.get(category, 0) + 1
        else:
            avg_wqi = 0
            wqi_categories = {}
        
        return {
            "success": True,
            "statistics": {
                "total_readings": total_readings,
                "unique_devices": unique_devices,
                "active_alerts": active_alerts,
                "average_wqi": round(avg_wqi, 2),
                "wqi_distribution": wqi_categories
            },
            "note": "Statistics from in-memory data only"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

@app.delete("/api/v1/clear-data")
async def clear_all_data():
    """
    Clear all in-memory data (useful for testing)
    """
    global readings_storage, alerts_storage
    readings_count = len(readings_storage)
    alerts_count = len(alerts_storage)
    
    readings_storage = []
    alerts_storage = []
    
    return {
        "success": True,
        "message": "All data cleared",
        "cleared": {
            "readings": readings_count,
            "alerts": alerts_count
        }
    }

# Batch prediction endpoint
@app.post("/api/v1/predict/batch")
async def batch_predict(data_list: List[SensorData]):
    """
    Analyze multiple water samples at once
    """
    try:
        results = []
        for data in data_list:
            sensor_dict = {
                'ph': data.ph,
                'tds': data.tds,
                'turbidity': data.turbidity,
                'temperature': data.temperature,
                'do': data.do
            }
            
            prediction = predictor.analyze_water_sample(sensor_dict)
            prediction['location'] = data.location
            prediction['device_id'] = data.device_id
            
            results.append(prediction)
        
        return {
            "success": True,
            "count": len(results),
            "data": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")

# Run server
if __name__ == "__main__":
    print("="*60)
    print("🌊 Water Quality ML Backend Starting...")
    print("="*60)
    print("📍 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("="*60)
    print("\n⚠️  NOTE: Using in-memory storage (no database)")
    print("   Data will be lost when server restarts!\n")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
