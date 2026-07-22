import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.backend.models.database import Base
from app.backend.models.domain import (
    User, Machine, UserRole, MachineStatus, 
    MaintenanceTask, MaintenanceStatus, Alert, AlertSeverity, ModelRegistry
)

DATABASE_URL = "postgresql://admin:secret@127.0.0.1:5433/predictive_maintenance"

def seed_platform_database():
    print("Connecting to database container on port 5433...")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        print("Resetting database schema...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        print("Seeding Users...")
        admin_user = User(
            name="Narayana Hrithik Raj",
            email="admin@enterprise.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36XU8BBYpXW8BBYpXW8BBYp", # 'secret'
            role=UserRole.ADMIN,
            is_active=True
        )
        operator_user = User(
            name="Operations Engineer",
            email="user@enterprise.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36XU8BBYpXW8BBYpXW8BBYp", # 'secret'
            role=UserRole.USER,
            is_active=True
        )
        db.add(admin_user)
        db.add(operator_user)
        db.commit()

        print("Seeding Machines with Assignments...")
        machines = [
            Machine(
                name="CNC Milling Axis-A", 
                type="CNC Machine", 
                manufacturer="Siemens", 
                location="Plant 1", 
                department="Machining", 
                status=MachineStatus.HEALTHY,
                assigned_user_id=operator_user.id,
                health_score=94.2,
                rul_days=182.0,
                operating_hours=1420.5
            ),
            Machine(
                name="High-Pressure Coolant Pump", 
                type="Hydraulic Pump", 
                manufacturer="Bosch", 
                location="Plant 1", 
                department="Cooling", 
                status=MachineStatus.AT_RISK,
                assigned_user_id=operator_user.id,
                health_score=68.5,
                rul_days=24.5,
                operating_hours=3210.0
            ),
            Machine(
                name="Main Assembly Rotor Turbine", 
                type="Gas Turbine", 
                manufacturer="GE Digital", 
                location="Plant 2", 
                department="Power Gen", 
                status=MachineStatus.CRITICAL,
                assigned_user_id=admin_user.id,
                health_score=32.0,
                rul_days=4.1,
                operating_hours=8920.0
            ),
            Machine(
                name="Robotic Welding Arm Element", 
                type="Articulated Robot", 
                manufacturer="Tata Advanced Systems", 
                location="Plant 2", 
                department="Assembly", 
                status=MachineStatus.HEALTHY,
                assigned_user_id=operator_user.id,
                health_score=98.0,
                rul_days=310.0,
                operating_hours=650.0
            )
        ]
        for m in machines:
            db.add(m)
        db.commit()

        print("Seeding Maintenance Tasks & Alerts...")
        task = MaintenanceTask(
            machine_id=machines[1].id,
            assigned_user_id=operator_user.id,
            task_description="Inspect coolant fluid pressure seals and replace worn gaskets.",
            priority="HIGH",
            status=MaintenanceStatus.SCHEDULED,
            scheduled_date=datetime.utcnow() + timedelta(days=2),
            estimated_downtime_hours=3.5,
            estimated_savings_usd=1200.0
        )
        alert = Alert(
            machine_id=machines[2].id,
            title="Critical Bearing Vibration Exceeded",
            message="Vibration frequency spike above 4.2 g detected on Turbine Rotor 1.",
            severity=AlertSeverity.CRITICAL,
            is_resolved=False
        )
        model = ModelRegistry(
            model_name="XGBoost-Failure-Predictor",
            version="v2.1.0",
            framework="XGBoost CPU",
            accuracy=0.964,
            f1_score=0.951,
            is_deployed=True
        )
        db.add(task)
        db.add(alert)
        db.add(model)
        db.commit()

        print("✅ Database seeding complete! All core structures initialized.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_platform_database()