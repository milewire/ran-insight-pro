from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="analyst")  # admin, analyst, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    uploads = relationship("Upload", back_populates="user")

class Upload(Base):
    __tablename__ = "uploads"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(100), ForeignKey("users.user_id"), nullable=True)
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed
    
    # Relationships
    user = relationship("User", back_populates="uploads")
    kpi_data = relationship("KPIData", back_populates="upload")
    analysis_results = relationship("AnalysisResult", back_populates="upload")

class KPIData(Base):
    __tablename__ = "kpi_data"
    
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    rtwp = Column(Float, nullable=True)
    sinr = Column(Float, nullable=True)
    prb = Column(Float, nullable=True)
    node_id = Column(String(100), nullable=True)
    cluster_id = Column(String(50), nullable=True)
    
    # Relationships
    upload = relationship("Upload", back_populates="kpi_data")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Statistical summaries
    rtwp_mean = Column(Float, nullable=True)
    rtwp_std = Column(Float, nullable=True)
    sinr_mean = Column(Float, nullable=True)
    sinr_std = Column(Float, nullable=True)
    prb_mean = Column(Float, nullable=True)
    prb_std = Column(Float, nullable=True)
    
    # Anomaly detection results
    rtwp_anomalies = Column(Integer, default=0)
    sinr_anomalies = Column(Integer, default=0)
    prb_anomalies = Column(Integer, default=0)
    
    # Correlation analysis
    rtwp_sinr_correlation = Column(Float, nullable=True)
    rtwp_prb_correlation = Column(Float, nullable=True)
    sinr_prb_correlation = Column(Float, nullable=True)
    
    # AI Analysis
    ai_summary = Column(Text, nullable=True)
    ai_confidence = Column(Float, nullable=True)
    ai_diagnosis = Column(Text, nullable=True)
    
    # Relationships
    upload = relationship("Upload", back_populates="analysis_results")

class FirmwareLog(Base):
    __tablename__ = "firmware_log"
    
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String(100), nullable=False, index=True)
    ru_version = Column(String(50), nullable=True)
    bb_version = Column(String(50), nullable=True)
    firmware_date = Column(DateTime, nullable=True)
    log_timestamp = Column(DateTime, default=datetime.utcnow)
    is_valid = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)

class HealthCheck(Base):
    __tablename__ = "health_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    check_timestamp = Column(DateTime, default=datetime.utcnow)
    api_status = Column(String(20), default="healthy")
    db_status = Column(String(20), default="healthy")
    ai_service_status = Column(String(20), default="healthy")
    response_time_ms = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
