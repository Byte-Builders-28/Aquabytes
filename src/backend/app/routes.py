from fastapi import APIRouter, HTTPException, Query, status
from datetime import datetime
from typing import List, Dict, Optional
import time

from app.models import SensorData, PingResponse, RainRequest, WaterInput
from ml.predictor import WaterQualityPredictor
from ml.water_budget_model import predict_water_risk
from utils.json import JSONDB
from utils.rainfall_engine import get_RTWH
from utils.weather import get_next5days_rain
from utils.location import get_location_details, get_address_from_coords

router = APIRouter()

predictor = WaterQualityPredictor()
db = JSONDB("database.json")


# ============================================================
# SYSTEM
# ============================================================

@router.get("/")
async def root():
    return {
        "message": "Water Quality ML Backend API",
        "version": "2.0.0",
        "status": "operational"
    }


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


@router.delete("/api/v1/system/data")
async def clear_system_data():
    db.clear_all()
    return {"success": True, "message": "All data cleared"}


# ============================================================
# GEOLOCATION
# ============================================================

@router.get("/geocode")
def geocode(
    address: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None)
):
    if address:
        result = get_location_details(address)
        if not result:
            raise HTTPException(404, f"Could not find coordinates for: {address}")
        return {"mode": "forward", **result}

    if lat is not None and lng is not None:
        result = get_address_from_coords(lat, lng)
        if not result:
            raise HTTPException(404, "Could not find address for coordinates")
        return {"mode": "reverse", **result}

    raise HTTPException(400, "Provide either address or lat and lng")


# ============================================================
# RAINWATER HARVESTING
# ============================================================

@router.post("/api/v1/rtwh/recommendation")
def rainwater_recommendation(req: RainRequest):
    area_m2 = req.area * 0.092903

    return get_RTWH(
        area_m2=area_m2,
        population=req.population,
        budget=req.budget,
        state=req.state,
        city=req.city,
        rooftype=req.roof
    )


# ============================================================
# WATER RISK (USAGE + RELIABILITY)
# ============================================================

@router.post("/api/v1/water-risk/{device_id}")
def water_risk_prediction(data: WaterInput, device_id: str):
    rain_next7 = get_next5days_rain(data.state, data.city)
    dry_days = 0 if max(rain_next7) > 0 else 7

    readings = db.get_readings()
    device_readings = [r for r in readings if r.get("device_id") == device_id]

    if not device_readings:
        raise HTTPException(404, "No readings found for device")

    latest = device_readings[-1]
    sensor = latest["sensor_data"]

    return predict_water_risk(
        tank_cap=data.tank_cap,
        current_level=data.current_level,
        dwellers=data.population,
        avg_need=data.avg_need,
        rain_next7_list=rain_next7,
        dry_days=dry_days,
        ph=sensor["ph"],
        tds=sensor["tds"]
    )


# ============================================================
# WATER QUALITY PREDICTION
# ============================================================

@router.post("/api/v1/water-quality/manual/predict")
async def predict_water_quality(data: SensorData):
    sensor = {
        "ph": data.ph,
        "tds": data.tds,
        "turbidity": data.turbidity,
        "temperature": data.temperature,
        "do": data.do
    }

    result = predictor.analyze_water_sample(sensor)

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

    return {"success": True, "data": result}


@router.post("/api/v1/devices/{device_id}/water-quality/predict")
async def predict_latest_for_device(device_id: str):
    readings = db.get_readings()
    device_readings = [r for r in readings if r["device_id"] == device_id]

    if not device_readings:
        raise HTTPException(404, "No readings found")

    latest = device_readings[-1]
    sensor = latest["sensor_data"]

    result = predictor.analyze_water_sample(sensor)

    db.update_reading(latest["id"], {
        "prediction": {
            "wqi": result["wqi"]["wqi"],
            "wqi_category": result["wqi"]["category"],
            "microbial_risk_level": result["microbial_risk"]["level"],
            "heavy_metal_risk_level": result["heavy_metal_risk"]["level"],
            "irrigation_suitable": result["irrigation_suitable"]["suitable"]
        }
    })

    return {"success": True, "data": result}


# ============================================================
# DEVICE MANAGEMENT
# ============================================================

@router.post("/api/v1/devices/register", status_code=status.HTTP_201_CREATED)
def register_device(payload: SensorData):
    device_id = payload.device_id or "unknown"

    readings = db.get_readings()
    reading_id = len(readings) + 1

    entry = {
        "id": reading_id,
        "device_id": device_id,
        "sensor_data": payload.dict(),
        "timestamp": int(time.time())
    }

    db.add_reading(entry)

    return {"status": "device_registered", "device_id": device_id}


@router.get("/api/v1/devices/{device_id}/sensor/latest")
async def latest_sensor_data(device_id: str):
    readings = db.get_readings()
    device_readings = [r for r in readings if r["device_id"] == device_id]

    if not device_readings:
        raise HTTPException(404, "No readings found")

    latest = device_readings[-1]

    return {
        "success": True,
        "timestamp": latest["timestamp"],
        "sensor_data": latest["sensor_data"]
    }


@router.get("/api/v1/devices/{device_id}/history")
async def device_history(device_id: str, limit: int = 100):
    readings = db.get_readings()
    device_readings = [r for r in readings if r["device_id"] == device_id]

    return {
        "success": True,
        "count": min(len(device_readings), limit),
        "data": list(reversed(device_readings))[:limit]
    }


@router.get("/api/v1/devices/{device_id}/alerts")
async def device_alerts(device_id: str, resolved: bool = False):
    alerts = db.get_alerts()

    result = [
        a for a in alerts
        if a["device_id"] == device_id and (resolved or not a["is_resolved"])
    ]

    result.sort(key=lambda x: x["created_at"], reverse=True)

    return {"success": True, "alerts": result[:50]}


@router.put("/api/v1/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int):
    db.update_alert(alert_id, {
        "is_resolved": True,
        "resolved_at": datetime.utcnow().isoformat()
    })

    return {"success": True, "alert_id": alert_id}