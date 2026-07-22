import shap
import joblib
import numpy as np

class MaintenanceExplainer:
    def __init__(self, model_path: str, feature_names: list):
        self.feature_names = feature_names
        # 1. Properly load and assign the model binary to an instance attribute
        self.model = joblib.load(model_path)
        
        # Use localized TreeSHAP for hyper-fast calculation overhead
        self.explainer = shap.TreeExplainer(self.model)

    def explain_instance(self, scaled_features_row) -> dict:
        """
        Calculates local feature contribution values for a single real-time machine snapshot.
        """
        # Calculate raw SHAP values
        raw_shap_values = self.explainer.shap_values(scaled_features_row)
        
        # Handle binary classification array shapes safely across library versions
        if isinstance(raw_shap_values, list):
            # Take the impact values driving class 1 (Failure Prediction)
            shap_array = raw_shap_values[1][0] if len(raw_shap_values) > 1 else raw_shap_values[0][0]
        elif len(raw_shap_values.shape) == 3:
            shap_array = raw_shap_values[0, :, 1]
        else:
            shap_array = raw_shap_values[0]

        # Format feature importances dynamically for JSON API consumption
        feature_contributions = dict(zip(self.feature_names, shap_array))
        
        # Sort descending by absolute impact magnitude
        sorted_contributions = dict(
            sorted(feature_contributions.items(), key=lambda item: abs(item[1]), reverse=True)
        )
        
        return sorted_contributions