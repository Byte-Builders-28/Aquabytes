from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SensorData(BaseModel):
    ph: float = Field(..., ge=0, le=14, description="pH value (0-14)")
    tds: float = Field(..., ge=0, description="Total Dissolved Solids in ppm")
    turbidity: float = Field(..., ge=0, description="Turbidity in NTU")
    temperature: float = Field(..., ge=-10, le=60, description="Temperature in Celsius")
    do: float = Field(..., ge=0, le=20, description="Dissolved Oxygen in mg/L", alias="dissolved_oxygen")
    location: Optional[str] = None
    device_id: Optional[str] = None

class HistoricalDataQuery(BaseModel):
    device_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, le=1000)
