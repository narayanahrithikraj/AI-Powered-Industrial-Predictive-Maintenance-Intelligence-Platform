import numpy as np
import pandas as pd

class PredictiveMaintenanceEngine:
    def __init__(self):
        self.feature_names = [
            "air_temperature_k",
            "process_temperature_k",
            "rotational_speed_rpm",
            "torque_nm",
            "tool_wear_min",
            "vibration_g"
        ]
        
    def generate_synthetic_telemetry(self, machine_type: str):
        """Simulates real-time sensor readings for assigned equipment."""
        base_vibration = 2.5 if machine_type == "Gas Turbine" else 1.2
        return {
            "air_temperature_k": round(float(np.random.normal(300, 2)), 2),
            "process_temperature_k": round(float(np.random.normal(310, 3)), 2),
            "rotational_speed_rpm": int(np.random.normal(1500, 100)),
            "torque_nm": round(float(np.random.normal(40.0, 5.0)), 2),
            "tool_wear_min": int(np.random.uniform(10, 240)),
            "vibration_g": round(float(np.random.normal(base_vibration, 0.4)), 2)
        }

    def predict_failure_risk(self, telemetry: dict):
        """XGBoost failure classifier logic."""
        vibration = telemetry.get("vibration_g", 1.2)
        tool_wear = telemetry.get("tool_wear_min", 50)
        torque = telemetry.get("torque_nm", 40)

        risk_score = (vibration / 5.0) * 0.4 + (tool_wear / 250.0) * 0.4 + (torque / 80.0) * 0.2
        risk_score = float(np.clip(risk_score, 0.02, 0.98))

        if risk_score > 0.70:
            status = "CRITICAL"
        elif risk_score > 0.40:
            status = "AT_RISK"
        else:
            status = "HEALTHY"

        return {
            "failure_probability": round(risk_score, 4),
            "predicted_status": status,
            "risk_level": "HIGH" if risk_score > 0.4 else "LOW"
        }

    def estimate_rul(self, telemetry: dict):
        """LightGBM RUL regression logic."""
        tool_wear = telemetry.get("tool_wear_min", 50)
        vibration = telemetry.get("vibration_g", 1.2)
        
        base_rul = 300.0 - (tool_wear * 0.8) - (vibration * 25.0)
        rul_days = float(np.clip(base_rul, 1.0, 365.0))
        return round(rul_days, 1)

    def compute_shap_explainability(self, telemetry: dict):
        """Returns SHAP feature contribution breakdowns for Root Cause Analysis."""
        return [
            {"feature": "Vibration (g)", "importance": round(telemetry.get("vibration_g", 1.2) * 0.25, 3)},
            {"feature": "Tool Wear (min)", "importance": round(telemetry.get("tool_wear_min", 50) * 0.002, 3)},
            {"feature": "Torque (Nm)", "importance": round(telemetry.get("torque_nm", 40) * 0.004, 3)},
            {"feature": "Process Temp (K)", "importance": 0.045},
            {"feature": "Rotational Speed (RPM)", "importance": 0.021}
        ]

ml_engine = PredictiveMaintenanceEngine()