from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, DateTime, ARRAY, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/water_quality_db')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SensorReading(Base):
    __tablename__ = 'sensor_readings'
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), nullable=False, index=True)
    location = Column(String(100))
    ph = Column(Float, nullable=False)
    tds = Column(Float, nullable=False)
    turbidity = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    dissolved_oxygen = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    predictions = relationship("Prediction", back_populates="reading")

class Prediction(Base):
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True, index=True)
    reading_id = Column(Integer, ForeignKey('sensor_readings.id'))
    wqi = Column(Float, nullable=False)
    wqi_category = Column(String(20))
    microbial_risk_score = Column(Integer)
    microbial_risk_level = Column(String(20))
    heavy_metal_risk_score = Column(Integer)
    heavy_metal_risk_level = Column(String(20))
    irrigation_suitable = Column(Boolean)
    irrigation_score = Column(Float)
    alerts = Column(ARRAY(Text))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    reading = relationship("SensorReading", back_populates="predictions")

class Alert(Base):
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(50), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
Base.metadata.create_all(bind=engine)
