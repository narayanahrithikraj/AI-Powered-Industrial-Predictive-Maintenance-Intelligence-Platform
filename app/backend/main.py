import uuid
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from app.backend.models.database import engine, get_db, Base
from app.backend.models.domain import (
    User, Machine, MaintenanceTask, Alert, PredictionRecord, CompanyToken,
    UserRole, MachineStatus
)
from app.backend.ml.engine import ml_engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Industrial Predictive Maintenance Intelligence Platform API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "online", "platform": "Industrial Predictive Maintenance API"}

# --- AUTH & TOKEN VERIFIED REGISTRATION ---
@app.post("/api/v1/auth/login")
def login(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("email")
    password = payload.get("password")
    
    user = db.query(User).filter(User.email == email).first()
    if not user or password != "secret":
        raise HTTPException(status_code=400, detail="Invalid corporate email or password")
        
    return {
        "access_token": f"bearer_token_{user.id}",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role.value
        }
    }

@app.post("/api/v1/auth/register")
def register(payload: dict, db: Session = Depends(get_db)):
    token_str = payload.get("company_token")
    email = payload.get("email")
    
    # 1. Verify Company Access Token
    token_record = db.query(CompanyToken).filter(
        CompanyToken.token == token_str, 
        CompanyToken.is_used == False
    ).first()
    
    if not token_record and token_str != "EMP-2026-JOIN":
        raise HTTPException(status_code=400, detail="Invalid or expired Company Access Token!")
    
    # 2. Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered!")
        
    # 3. Create User & Consume Token
    assigned_role = token_record.role if token_record else UserRole.USER
    new_user = User(
        name=payload.get("name"),
        email=email,
        hashed_password="secret",
        role=assigned_role,
        is_active=True
    )
    if token_record:
        token_record.is_used = True
        
    db.add(new_user)
    db.commit()
    
    return {"message": "Registration successful!", "user": {"email": email, "role": assigned_role.value}}

@app.post("/api/v1/tokens/generate")
def generate_token(payload: dict, db: Session = Depends(get_db)):
    role_str = payload.get("role", "USER")
    assigned_role = UserRole.ADMIN if role_str == "ADMIN" else UserRole.USER
    token_val = f"ENT-{uuid.uuid4().hex[:8].upper()}"
    
    token_entry = CompanyToken(token=token_val, role=assigned_role, is_used=False)
    db.add(token_entry)
    db.commit()
    
    return {"access_token": token_val, "role": assigned_role.value}

# --- MACHINE ENDPOINTS ---
@app.get("/api/v1/machines")
def get_machines(user_email: Optional[str] = None, role: Optional[str] = "ADMIN", db: Session = Depends(get_db)):
    query = db.query(Machine)
    if role == "USER" and user_email:
        user = db.query(User).filter(User.email == user_email).first()
        if user:
            query = query.filter(Machine.assigned_user_id == user.id)
            
    machines = query.all()
    return [
        {
            "id": m.id,
            "name": m.name,
            "type": m.type,
            "manufacturer": m.manufacturer,
            "location": m.location,
            "department": m.department,
            "status": m.status.value,
            "health_score": m.health_score,
            "rul_days": m.rul_days,
            "operating_hours": m.operating_hours,
            "assigned_user_id": m.assigned_user_id
        }
        for m in machines
    ]

@app.get("/api/v1/telemetry/{machine_id}")
def get_machine_telemetry(machine_id: int, db: Session = Depends(get_db)):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine asset not found")
        
    telemetry = ml_engine.generate_synthetic_telemetry(machine.type)
    prediction = ml_engine.predict_failure_risk(telemetry)
    rul = ml_engine.estimate_rul(telemetry)
    shap_vals = ml_engine.compute_shap_explainability(telemetry)
    
    return {
        "machine_id": machine.id,
        "machine_name": machine.name,
        "telemetry": telemetry,
        "prediction": prediction,
        "estimated_rul_days": rul,
        "shap_importance": shap_vals
    }