from fastapi import APIRouter, HTTPException
from typing import Dict, List
from datetime import datetime, timedelta

from ml.predictor import WaterQualityPredictor
from utils.json import JSONDB
from app.models import SensorData, HistoricalDataQuery

router = APIRouter()

# Predictor instance
predictor = WaterQualityPredictor()

# JSONDB instance
db = JSONDB("water_data.json")

# --- Root & Health ---
@router.get("/")
async def root():
    return {
        "message": "Water Quality ML Backend API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/api/v1/predict",
            "history": "/api/v1/history",
            "alerts": "/api/v1/alerts",
            "health": "/health"
        }
    }

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model": "loaded",
        "timestamp": datetime.now().isoformat(),
        "total_readings": len(db.get_readings()),
        "total_alerts": len(db.get_alerts())
    }

# --- Predict ---
@router.post("/api/v1/predict")
async def predict_water_quality(data: SensorData):
        sensor_dict = {
            'ph': data.ph,
            'tds': data.tds,
            'turbidity': data.turbidity,
            'temperature': data.temperature,
            'do': data.do
        }

        results = predictor.analyze_water_sample(sensor_dict)
        results['location'] = data.location
        results['device_id'] = data.device_id

        # Stor4e reading
        reading_id = len(db.get_readings()) + 1

        reading_entry = {
            "id": reading_id,
            "timestamp": results["timestamp"],
            "device_id": data.device_id or "unknown",
            "location": data.location,
            "sensor_data": sensor_dict,
            "prediction": {
                "wqi": results["wqi"]["wqi"],
                "wqi_category": results["wqi"]["category"],
                "microbial_risk_level": results["microbial_risk"]["level"],
                "heavy_metal_risk_level": results["heavy_metal_risk"]["level"],
                "irrigation_suitable": results["irrigation_suitable"]["suitable"]
            }
        }

        db.add_reading(reading_entry)

        # Store critical alerts
        for alert in results.get("alerts", []):
            if alert.get("severity") in ["high", "critical"]:
                alert_entry = {
                    "id": len(db.get_alerts()) + 1,
                    "device_id": data.device_id or "unknown",
                    "alert_type": alert.get("type"),
                    "severity": alert.get("severity"),
                    "message": alert.get("message"),
                    "created_at": datetime.now().isoformat(),
                    "is_resolved": False
                }
                db.add_alert(alert_entry)

        results["reading_id"] = reading_id
        return {"success": True, "data": results}

# --- Historical Data ---
@router.post("/api/v1/history")
async def get_historical_data(query: HistoricalDataQuery):
    try:
        readings = db.get_readings()
        if query.device_id:
            readings = [r for r in readings if r["device_id"] == query.device_id]
        if query.start_date:
            readings = [r for r in readings if r["timestamp"] >= query.start_date.isoformat()]
        if query.end_date:
            readings = [r for r in readings if r["timestamp"] <= query.end_date.isoformat()]

        readings = list(reversed(readings))[:query.limit]
        return {"success": True, "count": len(readings), "data": readings}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

# --- Alerts ---
@router.get("/api/v1/alerts/{device_id}")
async def get_device_alerts(device_id: str, resolved: bool = False):
    try:
        alerts = db.get_alerts()
        filtered = [a for a in alerts if a["device_id"] == device_id]
        if not resolved:
            filtered = [a for a in filtered if not a["is_resolved"]]
        filtered.sort(key=lambda x: x["created_at"], reverse=True)
        return {"success": True, "device_id": device_id, "count": len(filtered), "alerts": filtered[:50]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert retrieval error: {str(e)}")

@router.put("/api/v1/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int):
    try:
        alert = next((a for a in db.get_alerts() if a["id"] == alert_id), None)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        db.update_alert(alert_id, {"is_resolved": True, "resolved_at": datetime.now().isoformat()})
        return {"success": True, "message": "Alert resolved", "alert_id": alert_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resolution error: {str(e)}")

# --- Dashboard ---
def calculate_trends(readings: List[Dict]) -> Dict:
    if len(readings) < 2:
        return {"status": "insufficient_data"}
    mid = len(readings)//2
    first_half = readings[:mid]
    second_half = readings[mid:]
    trends = {}
    for param in ["ph", "tds", "turbidity", "temperature", "dissolved_oxygen"]:
        avg_first = sum(r["sensor_data"][param] for r in first_half)/len(first_half)
        avg_second = sum(r["sensor_data"][param] for r in second_half)/len(second_half)
        change_pct = ((avg_second - avg_first)/avg_first)*100 if avg_first > 0 else 0
        trends[param] = {
            "direction": "increasing" if change_pct > 5 else "decreasing" if change_pct < -5 else "stable",
            "change_percent": round(change_pct, 2)
        }
    return trends

@router.get("/api/v1/dashboard/{device_id}")
async def get_dashboard_data(device_id: str):
    try:
        readings = [r for r in db.get_readings() if r["device_id"] == device_id]
        if not readings:
            raise HTTPException(status_code=404, detail="No data found for device")
        latest = readings[-1]
        recent_24h = [r for r in readings if datetime.fromisoformat(r["timestamp"]) >= datetime.utcnow() - timedelta(days=1)]
        trends = calculate_trends(recent_24h)
        active_alerts = [a for a in db.get_alerts() if a["device_id"] == device_id and not a["is_resolved"]]

        return {
            "success": True,
            "device_id": device_id,
            "latest_reading": latest,
            "prediction": latest.get("prediction"),
            "trends": trends,
            "active_alerts": active_alerts,
            "readings_24h": len(recent_24h)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")

# --- Stats Summary ---
@router.get("/api/v1/stats/summary")
async def get_system_summary():
    try:
        readings = db.get_readings()
        alerts = db.get_alerts()
        total_readings = len(readings)
        total_devices = len(set(r["device_id"] for r in readings))
        active_alerts = sum(1 for a in alerts if not a["is_resolved"])
        recent_predictions = [r["prediction"]["wqi"] for r in readings[-100:] if r.get("prediction")]
        avg_wqi = sum(recent_predictions)/len(recent_predictions) if recent_predictions else 0
        wqi_distribution = {}
        for r in readings[-100:]:
            if r.get("prediction"):
                cat = r["prediction"]["wqi_category"]
                wqi_distribution[cat] = wqi_distribution.get(cat, 0)+1
        return {
            "success": True,
            "statistics": {
                "total_readings": total_readings,
                "total_devices": total_devices,
                "active_alerts": active_alerts,
                "average_wqi": round(avg_wqi, 2),
                "wqi_distribution": wqi_distribution
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")
