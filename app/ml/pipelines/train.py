import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, mean_absolute_error
from xgboost import XGBClassifier
from lightgbm import LGBMRegressor
from sklearn.ensemble import IsolationForest

# Ensure path targets exist
os.makedirs("app/ml/models", exist_ok=True)

def load_and_split_data(data_path: str):
    """
    Loads engineered features and sets up labels for multi-task learning.
    """
    df = pd.read_csv(data_path)
    
    # Features (Drop identifiers and raw labels)
    X = df.drop(columns=['machine_id', 'timestamp', 'is_failure', 'rul_hours'])
    
    # Labels for distinct tasks
    y_class = df['is_failure']  # 1 = Fail, 0 = Healthy
    y_reg = df['rul_hours']     # Continuous target for RUL
    
    return train_test_split(X, y_class, y_reg, test_size=0.2, random_state=42)

def train_predictive_maintenance_engine(data_path: str):
    # Unpack all variables explicitly within the local scope
    X_train, X_test, y_class_train, y_class_test, y_reg_train, y_reg_test = load_and_split_data(data_path)
    
    # Scale numerical features uniformly for stable inference
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    joblib.dump(scaler, "app/ml/models/scaler.joblib")
    
    print("--- Training Failure Prediction Model (XGBoost) ---")
    # Binary Classification Task
    clf_model = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.05, random_state=42)
    clf_model.fit(X_train_scaled, y_class_train)
    
    # Class Evaluation
    class_preds = clf_model.predict(X_test_scaled)
    print(f"Accuracy: {accuracy_score(y_class_test, class_preds):.4f}")
    print(classification_report(y_class_test, class_preds))
    joblib.dump(clf_model, "app/ml/models/failure_classifier.joblib")

    print("--- Training Remaining Useful Life Model (LightGBM) ---")
    # Regression Task
    reg_model = LGBMRegressor(n_estimators=150, max_depth=6, learning_rate=0.05, random_state=42) # type: ignore
    reg_model.fit(X_train_scaled, y_reg_train) # type: ignore
    
    # Regression Evaluation with explicit array casting to satisfy Pylance typing
    raw_preds = reg_model.predict(X_test_scaled) # type: ignore
    reg_preds = np.asarray(raw_preds, dtype=np.float64)
    y_true_reg = np.asarray(y_reg_test, dtype=np.float64)
    
    print(f"RUL MAE: {mean_absolute_error(y_true_reg, reg_preds):.2f} hours")
    print(f"RUL RMSE: {np.sqrt(mean_squared_error(y_true_reg, reg_preds)):.2f} hours")
    joblib.dump(reg_model, "app/ml/models/rul_regressor.joblib")

    print("--- Training Anomaly Detection Engine (Isolation Forest) ---")
    # Unsupervised Outlier Task (Train only on healthy operational data baseline)
    healthy_data = X_train_scaled[y_class_train == 0]
    anomaly_detector = IsolationForest(contamination=0.03, random_state=42)
    anomaly_detector.fit(healthy_data)
    joblib.dump(anomaly_detector, "app/ml/models/anomaly_detector.joblib")
    print("Anomaly Detection baseline model saved successfully.")

if __name__ == "__main__":
    # Placeholder path for initialization check
    print("ML Engine Pipeline Module compilation successful.")