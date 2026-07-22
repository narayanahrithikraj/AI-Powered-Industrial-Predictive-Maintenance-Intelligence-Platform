import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.backend.models.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class MachineStatus(str, enum.Enum):
    HEALTHY = "HEALTHY"
    AT_RISK = "AT_RISK"
    CRITICAL = "CRITICAL"
    DEACTIVATED = "DEACTIVATED"

class MaintenanceStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class AlertSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    photo_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    assigned_machines = relationship("Machine", back_populates="assigned_operator")
    maintenance_tasks = relationship("MaintenanceTask", back_populates="assigned_to_user")

class CompanyToken(Base):
    __tablename__ = "company_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(50), unique=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    manufacturer = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False)
    installation_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum(MachineStatus), default=MachineStatus.HEALTHY, nullable=False)
    
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    health_score = Column(Float, default=100.0)
    rul_days = Column(Float, default=365.0)
    operating_hours = Column(Float, default=0.0)
    last_maintenance_date = Column(DateTime, nullable=True)

    assigned_operator = relationship("User", back_populates="assigned_machines")
    predictions = relationship("PredictionRecord", back_populates="machine")
    maintenance_records = relationship("MaintenanceTask", back_populates="machine")

class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    task_description = Column(Text, nullable=False)
    priority = Column(String(20), default="MEDIUM")
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.SCHEDULED)
    scheduled_date = Column(DateTime, default=datetime.utcnow)
    completed_date = Column(DateTime, nullable=True)
    estimated_downtime_hours = Column(Float, default=2.0)
    estimated_savings_usd = Column(Float, default=500.0)

    machine = relationship("Machine", back_populates="maintenance_records")
    assigned_to_user = relationship("User", back_populates="maintenance_tasks")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.MEDIUM)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class PredictionRecord(Base):
    __tablename__ = "prediction_records"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    failure_probability = Column(Float, nullable=False)
    predicted_risk_level = Column(String(20), nullable=False)
    estimated_rul_days = Column(Float, nullable=False)
    is_anomaly = Column(Boolean, default=False)
    anomaly_severity = Column(Float, default=0.0)
    shap_summary_json = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    machine = relationship("Machine", back_populates="predictions")

class ModelRegistry(Base):
    __tablename__ = "model_registries"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    framework = Column(String(50), default="XGBoost/LightGBM")
    accuracy = Column(Float, nullable=False)
    f1_score = Column(Float, nullable=False)
    is_deployed = Column(Boolean, default=False)
    trained_at = Column(DateTime, default=datetime.utcnow)