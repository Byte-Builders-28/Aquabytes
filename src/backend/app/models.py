from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class SensorData(BaseModel):
    ph: float = Field(..., ge=0, le=14)
    tds: float = Field(..., ge=0)
    turbidity: float = Field(..., ge=0)
    temperature: float = Field(..., ge=-10, le=60)
    do: float = Field(..., ge=0, le=20)
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