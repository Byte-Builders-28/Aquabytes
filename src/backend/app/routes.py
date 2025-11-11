from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from ml.predictor import WaterQualityPredictor
from database.db import get_db, SensorReading, Prediction, Alert
from app.models import SensorData, HistoricalDataQuery

router = APIRouter()

# Use a predictor instance. If you prefer the app-scoped predictor in main, replace this with:
# predictor = request.app.state.predictor inside each endpoint.
predictor = WaterQualityPredictor()

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
        "timestamp": datetime.now().isoformat()
    }

@router.post("/api/v1/predict")
async def predict_water_quality(data: SensorData, db: Session = Depends(get_db)):
    try:
        sensor_dict = {
            'ph': data.ph,
            'tds': data.tds,
            'turbidity': data.turbidity,
            'temperature': data.temperature,
            'do': data.do
        }

        # Run ML prediction
        results = predictor.analyze_water_sample(sensor_dict)

        # Store sensor reading
        reading = SensorReading(
            device_id=data.device_id or "unknown",
            location=data.location,
            ph=data.ph,
            tds=data.tds,
            turbidity=data.turbidity,
            temperature=data.temperature,
            dissolved_oxygen=data.do
        )
        db.add(reading)
        db.flush()  # populate reading.id

        # Store prediction
        prediction = Prediction(
            reading_id=reading.id,
            wqi=results['wqi']['wqi'],
            wqi_category=results['wqi']['category'],
            microbial_risk_score=results['microbial_risk']['risk_score'],
            microbial_risk_level=results['microbial_risk']['level'],
            heavy_metal_risk_score=results['heavy_metal_risk']['risk_score'],
            heavy_metal_risk_level=results['heavy_metal_risk']['level'],
            irrigation_suitable=results['irrigation_suitable']['suitable'],
            irrigation_score=results['irrigation_suitable']['score'],
            alerts=[alert['message'] for alert in results.get('alerts', [])]
        )
        db.add(prediction)

        # Store critical alerts
        for alert in results.get('alerts', []):
            if alert.get('severity') in ['high', 'critical']:
                db_alert = Alert(
                    device_id=data.device_id or "unknown",
                    alert_type=alert.get('type'),
                    severity=alert.get('severity'),
                    message=alert.get('message')
                )
                db.add(db_alert)

        db.commit()

        # Add metadata to results
        results['location'] = data.location
        results['device_id'] = data.device_id
        results['reading_id'] = reading.id

        return {"success": True, "data": results}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.post("/api/v1/history")
async def get_historical_data(query: HistoricalDataQuery, db: Session = Depends(get_db)):
    try:
        db_query = db.query(SensorReading)

        if query.device_id:
            db_query = db_query.filter(SensorReading.device_id == query.device_id)

        if query.start_date:
            db_query = db_query.filter(SensorReading.timestamp >= query.start_date)

        if query.end_date:
            db_query = db_query.filter(SensorReading.timestamp <= query.end_date)

        readings = db_query.order_by(SensorReading.timestamp.desc()).limit(query.limit).all()

        history = []
        for reading in readings:
            reading_data = {
                "id": reading.id,
                "device_id": reading.device_id,
                "location": reading.location,
                "timestamp": reading.timestamp.isoformat(),
                "sensor_data": {
                    "ph": reading.ph,
                    "tds": reading.tds,
                    "turbidity": reading.turbidity,
                    "temperature": reading.temperature,
                    "dissolved_oxygen": reading.dissolved_oxygen
                }
            }

            if getattr(reading, "predictions", None):
                pred = reading.predictions[0]
                reading_data["prediction"] = {
                    "wqi": pred.wqi,
                    "wqi_category": pred.wqi_category,
                    "microbial_risk_level": pred.microbial_risk_level,
                    "heavy_metal_risk_level": pred.heavy_metal_risk_level,
                    "irrigation_suitable": pred.irrigation_suitable
                }

            history.append(reading_data)

        return {"success": True, "count": len(history), "data": history}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

@router.get("/api/v1/alerts/{device_id}")
async def get_device_alerts(device_id: str, resolved: bool = False, db: Session = Depends(get_db)):
    try:
        query = db.query(Alert).filter(Alert.device_id == device_id)

        if not resolved:
            query = query.filter(Alert.is_resolved == False)

        alerts = query.order_by(Alert.created_at.desc()).limit(50).all()

        alert_list = [
            {
                "id": alert.id,
                "type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "created_at": alert.created_at.isoformat(),
                "resolved": alert.is_resolved
            }
            for alert in alerts
        ]

        return {"success": True, "device_id": device_id, "count": len(alert_list), "alerts": alert_list}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert retrieval error: {str(e)}")

@router.put("/api/v1/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    try:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()

        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")

        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        db.commit()

        return {"success": True, "message": "Alert resolved", "alert_id": alert_id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Resolution error: {str(e)}")

def calculate_trends(readings: List[SensorReading]) -> Dict:
    """Calculate parameter trends"""
    if len(readings) < 2:
        return {"status": "insufficient_data"}

    first_half = readings[:len(readings)//2]
    second_half = readings[len(readings)//2:]

    def avg(items, attr):
        values = [getattr(item, attr) for item in items]
        return sum(values) / len(values) if values else 0

    trends = {}
    for param in ['ph', 'tds', 'turbidity', 'temperature', 'dissolved_oxygen']:
        avg_first = avg(first_half, param)
        avg_second = avg(second_half, param)

        if avg_first > 0:
            change_pct = ((avg_second - avg_first) / avg_first) * 100
            trends[param] = {
                "direction": "increasing" if change_pct > 5 else "decreasing" if change_pct < -5 else "stable",
                "change_percent": round(change_pct, 2)
            }

    return trends

@router.get("/api/v1/dashboard/{device_id}")
async def get_dashboard_data(device_id: str, db: Session = Depends(get_db)):
    try:
        latest = db.query(SensorReading).filter(
            SensorReading.device_id == device_id
        ).order_by(SensorReading.timestamp.desc()).first()

        if not latest:
            raise HTTPException(status_code=404, detail="No data found for device")

        day_ago = datetime.utcnow() - timedelta(days=1)
        recent_readings = db.query(SensorReading).filter(
            SensorReading.device_id == device_id,
            SensorReading.timestamp >= day_ago
        ).order_by(SensorReading.timestamp.asc()).all()

        active_alerts = db.query(Alert).filter(
            Alert.device_id == device_id,
            Alert.is_resolved == False
        ).order_by(Alert.created_at.desc()).all()

        trends = calculate_trends(recent_readings)

        latest_prediction = None
        if getattr(latest, "predictions", None):
            pred = latest.predictions[0]
            latest_prediction = {
                "wqi": pred.wqi,
                "wqi_category": pred.wqi_category,
                "microbial_risk": pred.microbial_risk_level,
                "heavy_metal_risk": pred.heavy_metal_risk_level,
                "irrigation_suitable": pred.irrigation_suitable
            }

        return {
            "success": True,
            "device_id": device_id,
            "latest_reading": {
                "timestamp": latest.timestamp.isoformat(),
                "ph": latest.ph,
                "tds": latest.tds,
                "turbidity": latest.turbidity,
                "temperature": latest.temperature,
                "dissolved_oxygen": latest.dissolved_oxygen
            },
            "prediction": latest_prediction,
            "trends": trends,
            "active_alerts": [
                {"type": a.alert_type, "severity": a.severity, "message": a.message, "created_at": a.created_at.isoformat()}
                for a in active_alerts
            ],
            "readings_24h": len(recent_readings)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")

@router.get("/api/v1/stats/summary")
async def get_system_summary(db: Session = Depends(get_db)):
    try:
        total_readings = db.query(SensorReading).count()
        total_devices = db.query(SensorReading.device_id).distinct().count()
        active_alerts = db.query(Alert).filter(Alert.is_resolved == False).count()

        recent_predictions = db.query(Prediction).order_by(
            Prediction.timestamp.desc()
        ).limit(100).all()

        if recent_predictions:
            avg_wqi = sum(p.wqi for p in recent_predictions) / len(recent_predictions)
            wqi_categories = {}
            for p in recent_predictions:
                wqi_categories[p.wqi_category] = wqi_categories.get(p.wqi_category, 0) + 1
        else:
            avg_wqi = 0
            wqi_categories = {}

        return {
            "success": True,
            "statistics": {
                "total_readings": total_readings,
                "total_devices": total_devices,
                "active_alerts": active_alerts,
                "average_wqi": round(avg_wqi, 2),
                "wqi_distribution": wqi_categories
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")
