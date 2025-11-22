from fastapi import APIRouter, HTTPException, Query, status
from datetime import datetime
from typing import List, Dict, Optional
from app.models import SensorData, PingResponse
from ml.predictor import WaterQualityPredictor
from utils.json import JSONDB

import time

router = APIRouter()

predictor = WaterQualityPredictor()
db = JSONDB("database.json")

# -------------------------------------------------------------
# ROOT
# -------------------------------------------------------------
@router.get("/")
async def root():
    return {
        "message": "Water Quality ML Backend API (JSON DB)",
        "version": "2.0.0",
        "status": "operational",
        "db_file": "database.json"
    }

# -------------------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------------------
@router.get("/health")
async def health_check():
    readings = db.get_readings()
    alerts = db.get_alerts()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "total_readings": len(readings),
        "total_alerts": len(alerts)
    }

# -------------------------------------------------------------
# PREDICT AND STORE READING
# -------------------------------------------------------------
@router.post("/api/v1/predict_manual")
async def predict_water_quality(data: SensorData):
    try:
        sensor = {
            "ph": data.ph,
            "tds": data.tds,
            "turbidity": data.turbidity,
            "temperature": data.temperature,
            "do": data.do
        }

        result = predictor.analyze_water_sample(sensor)
        result["location"] = data.location
        result["device_id"] = data.device_id

        readings = db.get_readings()
        reading_id = len(readings) + 1

        entry = {
            "id": reading_id,
            "timestamp": datetime.utcnow().isoformat(),
            "device_id": data.device_id,
            "location": data.location,
            "sensor_data": sensor,
            "prediction": {
                "wqi": result["wqi"]["wqi"],
                "wqi_category": result["wqi"]["category"],
                "microbial_risk_level": result["microbial_risk"]["level"],
                "heavy_metal_risk_level": result["heavy_metal_risk"]["level"],
                "irrigation_suitable": result["irrigation_suitable"]["suitable"]
            }
        }

        db.add_reading(entry)

        # Store alerts
        for alert in result["alerts"]:
            if alert["severity"] in ["high", "critical"]:
                alerts = db.get_alerts()
                alert_id = len(alerts) + 1
                db.add_alert({
                    "id": alert_id,
                    "device_id": data.device_id,
                    "alert_type": alert["type"],
                    "severity": alert["severity"],
                    "message": alert["message"],
                    "created_at": datetime.utcnow().isoformat(),
                    "is_resolved": False
                })

        return {"success": True, "data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/predict/latest/{device_id}")
async def predict_latest(device_id: str):
    try:
        readings = db.get_readings()

        # Filter readings for this device
        device_readings = [r for r in readings if r.get("device_id") == device_id]

        if not device_readings:
            raise HTTPException(status_code=404, detail="No readings found for device")

        # Get latest entry
        latest = device_readings[-1]
        sensor = latest.get("sensor_data")

        if not sensor:
            raise HTTPException(status_code=400, detail="Latest entry has no sensor_data")

        # Run prediction
        result = predictor.analyze_water_sample(sensor)

        updated_prediction = {
            "wqi": result["wqi"]["wqi"],
            "wqi_category": result["wqi"]["category"],
            "microbial_risk_level": result["microbial_risk"]["level"],
            "heavy_metal_risk_level": result["heavy_metal_risk"]["level"],
            "irrigation_suitable": result["irrigation_suitable"]["suitable"]
        }

        # Update DB reading
        db.update_reading(latest["id"], {
            "prediction": updated_prediction
        })

        return {
            "success": True,
            "device_id": device_id,
            "timestamp": latest["timestamp"],
            "sensor_data": sensor,
            "data" : result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------
# IoT: Register Device
# --------------------------
@router.post("/iot/register", status_code=status.HTTP_201_CREATED)
def register_device(payload: SensorData):
    device_id = payload.device_id or "unknown"
    sensor_data = payload.dict()

    readings = db.get_readings()
    reading_id = len(readings) + 1

    entry = {
        "id": reading_id,
        "device_id": device_id,
        "sensor_data": sensor_data,
        "timestamp": int(time.time())
    }

    db.add_reading(entry)

    return {"status": "device_registered", "device_id": device_id}



# --------------------------
# IoT: Device Heartbeat / Ping
# --------------------------
@router.post("/iot/ping")
def iot_ping(payload: PingResponse):
    device_id = payload.device_id
    status = payload.status

    if not device_id:
        raise HTTPException(status_code=400, detail="device_id is required")

    timestamp = int(time.time())  # current timestamp in seconds

    # Save as alert entry
    db.add_alert({
        "id": timestamp,
        "device_id": device_id,
        "alert_type": "heartbeat",
        "severity": "low",
        "message": f"Device ping received with status '{status}'",
        "is_resolved": False,
        "created_at": timestamp,
        "resolved_at": None
    })

    return {
        "status": "pong",
        "device_id": device_id,
        "received_status": status,
        "timestamp": timestamp
    }


# -------------------------------------------------------------
# GET HISTORY
# -------------------------------------------------------------
@router.get("/api/v1/history")
async def get_historical_data(device_id: Optional[str] = None, limit: int = 100):
    try:
        readings = db.get_readings()
        if device_id:
            readings = [r for r in readings if r["device_id"] == device_id]

        return {
            "success": True,
            "count": min(len(readings), limit),
            "data": list(reversed(readings))[:limit]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------------------
# GET ALERTS
# -------------------------------------------------------------
@router.get("/api/v1/alerts/{device_id}")
async def get_alerts(device_id: str, resolved: bool = False):
    try:
        alerts = db.get_alerts()
        result = [
            a for a in alerts
            if a["device_id"] == device_id and (resolved or not a["is_resolved"])
        ]

        result.sort(key=lambda x: x["created_at"], reverse=True)
        return {"success": True, "alerts": result[:50]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------------------
# RESOLVE ALERT
# -------------------------------------------------------------
@router.put("/api/v1/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int):
    try:
        db.update_alert(alert_id, {
            "is_resolved": True,
            "resolved_at": datetime.utcnow().isoformat()
        })
        return {"success": True, "alert_id": alert_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------------------
# DASHBOARD DATA
# -------------------------------------------------------------
@router.get("/api/v1/dashboard/{device_id}")
async def get_dashboard_data(device_id: str):
    try:
        readings = db.get_readings()
        device_data = [r for r in readings if r["device_id"] == device_id]
        if not device_data:
            raise HTTPException(status_code=404, detail="No data found")

        latest = device_data[-1]
        recent = device_data[-10:]
        trends = calculate_trends(recent)

        alerts = db.get_alerts()
        active = [
            a for a in alerts if a["device_id"] == device_id and not a["is_resolved"]
        ]

        return {
            "success": True,
            "latest_reading": {
                "timestamp": latest["timestamp"],
                **latest["sensor_data"]
            },
            "prediction": latest["prediction"],
            "trends": trends,
            "active_alerts": active,
            "total_readings": len(device_data)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------------------
# TRENDS
# -------------------------------------------------------------
def calculate_trends(readings: List[Dict]) -> Dict:
    if len(readings) < 2:
        return {"status": "insufficient_data"}

    mid = len(readings) // 2
    first, second = readings[:mid], readings[mid:]

    def avg(items, key):
        v = [i["sensor_data"][key] for i in items]
        return sum(v) / len(v)

    trends = {}
    params = ["ph", "tds", "turbidity", "temperature", "do"]

    for p in params:
        a1, a2 = avg(first, p), avg(second, p)
        if a1 == 0:
            continue
        pct = ((a2 - a1) / a1) * 100
        trends[p] = {
            "direction": "increasing" if pct > 5 else "decreasing" if pct < -5 else "stable",
            "change_percent": round(pct, 2)
        }

    return trends

# -------------------------------------------------------------
# STATS SUMMARY
# -------------------------------------------------------------
@router.get("/api/v1/stats/summary")
async def get_system_summary():
    try:
        readings = db.get_readings()
        alerts = db.get_alerts()

        total = len(readings)
        unique = len(set(r["device_id"] for r in readings))
        active = sum(1 for a in alerts if not a["is_resolved"])

        if total:
            last100 = readings[-100:]
            avg_wqi = sum(r["prediction"]["wqi"] for r in last100) / len(last100)

            dist = {}
            for r in last100:
                c = r["prediction"]["wqi_category"]
                dist[c] = dist.get(c, 0) + 1

        else:
            avg_wqi = 0
            dist = {}

        return {
            "success": True,
            "statistics": {
                "total_readings": total,
                "unique_devices": unique,
                "active_alerts": active,
                "average_wqi": round(avg_wqi, 2),
                "wqi_distribution": dist
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------------------
# CLEAR DATA
# -------------------------------------------------------------
@router.delete("/api/v1/clear-data")
async def clear_all_data():
    db.clear_all()
    return {"success": True, "message": "All data cleared"}

# -------------------------------------------------------------
# BATCH PREDICTION
# -------------------------------------------------------------
@router.post("/api/v1/predict/batch")
async def batch_predict(data_list: List[SensorData]):
    try:
        results = []
        for data in data_list:
            sensor = {
                "ph": data.ph,
                "tds": data.tds,
                "turbidity": data.turbidity,
                "temperature": data.temperature,
                "do": data.do
            }
            pred = predictor.analyze_water_sample(sensor)
            pred["device_id"] = data.device_id
            pred["location"] = data.location
            results.append(pred)

        return {"success": True, "count": len(results), "data": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))