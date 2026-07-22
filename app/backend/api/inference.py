import os
import joblib
import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.backend.models import database, domain
from app.backend.core.security import get_current_user, RoleChecker
from app.ml.explainers.interpret import MaintenanceExplainer

router = APIRouter(prefix="/api/analytics", tags=["Industrial AI Analytics"])

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../ml/models"))
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.joblib")
CLASSIFIER_PATH = os.path.join(MODEL_DIR, "failure_classifier.joblib")
REGRESSOR_PATH = os.path.join(MODEL_DIR, "rul_regressor.joblib")
DETECTOR_PATH = os.path.join(MODEL_DIR, "anomaly_detector.joblib")

FEATURE_NAMES = [
    "temperature", "pressure", "vibration", "rpm",
    "temp_rolling_mean", "vibration_rolling_std", 
    "pressure_lag_1", "temp_pressure_ratio"
]

def load_ml_artifact(file_path: str):
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML Engine artifact missing. Please run model training tasks first."
        )
    return joblib.load(file_path)

@router.post("/evaluate/{machine_id}", status_code=status.HTTP_200_OK)
def evaluate_machine_telemetry(
    machine_id: int, 
    raw_telemetry: dict, 
    db: Session = Depends(database.get_db),
    current_user: domain.User = Depends(get_current_user)
):
    machine = db.query(domain.Machine).filter(domain.Machine.id == machine_id).first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine target ID not found.")

    try:
        input_data = {feat: [raw_telemetry.get(feat, 0.0)] for feat in FEATURE_NAMES}
        df_features = pd.DataFrame(input_data)
        
        scaler = load_ml_artifact(SCALER_PATH)
        classifier = load_ml_artifact(CLASSIFIER_PATH)
        regressor = load_ml_artifact(REGRESSOR_PATH)
        detector = load_ml_artifact(DETECTOR_PATH)
        
        scaled_row = scaler.transform(df_features)
        
        failure_prob = float(classifier.predict_proba(scaled_row)[0][1])
        rul_prediction = float(regressor.predict(scaled_row)[0])
        anomaly_flag = bool(detector.predict(scaled_row)[0] == -1)
        
        explainer = MaintenanceExplainer(CLASSIFIER_PATH, FEATURE_NAMES)
        shap_explanations = explainer.explain_instance(scaled_row)
        
        recommendation = "Operational telemetry matches optimal baselines. Keep scheduled intervals."
        priority = "Low"
        
        if failure_prob > 0.8 or anomaly_flag:
            priority = "Critical" if failure_prob > 0.9 else "High"
            if shap_explanations.get("vibration_rolling_std", 0) > shap_explanations.get("temp_rolling_mean", 0):
                recommendation = "CRITICAL WARNING: High mechanical vibration anomaly detected. Inspect main shaft bearing assembly immediately."
            else:
                recommendation = "HIGH RISKS WARNING: Thermal variance exceeds safety thresholds. Throttle operations load velocity."

        return {
            "machine_id": machine_id,
            "metrics": {
                "failure_probability": failure_prob,
                "predicted_remaining_useful_life_hours": max(0.0, rul_prediction),
                "is_anomaly_detected": anomaly_flag
            },
            "explainability": {
                "top_contributing_factors": shap_explanations
            },
            "actions": {
                "recommended_action": recommendation,
                "priority_level": priority
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))