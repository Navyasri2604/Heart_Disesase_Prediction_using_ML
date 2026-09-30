"""
CardioAI - Machine Learning service for predicting heart disease and generating Explainable AI insights.
"""
import json
from pathlib import Path
from threading import Lock

import joblib
import pandas as pd
from django.conf import settings
import shap

# Ordered features as expected by the model
FEATURES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", 
    "thalach", "exang", "oldpeak", "slope", "ca", "thal"
]

_artifact = None
_artifact_lock = Lock()


def load_artifact():
    """Load the trained model artifact with thread safety."""
    global _artifact
    if _artifact is None:
        with _artifact_lock:
            if _artifact is None:
                path = Path(settings.ML_MODEL_PATH)
                if not path.exists():
                    raise FileNotFoundError(
                        f"Trained model not found at {path}. Please run: python train_model.py"
                    )
                _artifact = joblib.load(path)
    return _artifact


def get_health_score(probability):
    """Calculates a health score out of 100 based on disease probability."""
    # Base score is 100. Lower probability of disease means higher score.
    # We use a non-linear scaling to penalize higher risk more.
    score = 100 - (probability * 100)
    return max(0, min(100, int(score)))


def get_risk_level(probability):
    """Determine clinical risk category."""
    if probability >= 0.85:
        return "critical"
    elif probability >= 0.60:
        return "high"
    elif probability >= 0.35:
        return "moderate"
    else:
        return "low"


def predict(features_dict):
    """
    Takes a dictionary of features, runs it through the loaded model pipeline, 
    and returns prediction, risk, and SHAP explanation.
    """
    artifact = load_artifact()
    pipeline = artifact["model"]
    model_name = artifact.get("model_name", "Unknown Model")
    
    # Create DataFrame for prediction
    row_data = {feature: [features_dict.get(feature, 0)] for feature in FEATURES}
    df = pd.DataFrame(row_data, columns=FEATURES)
    
    # Get probability and prediction
    # model classes_ usually [0, 1] where 1 is disease
    probabilities = pipeline.predict_proba(df)[0]
    
    # Default assumption: index 1 is positive class
    positive_index = 1
    if hasattr(pipeline.named_steps["classifier"], "classes_"):
        classes = list(pipeline.named_steps["classifier"].classes_)
        if 1 in classes:
            positive_index = classes.index(1)
            
    probability = float(probabilities[positive_index])
    prediction = bool(pipeline.predict(df)[0])
    
    # Compute Risk & Score
    risk_level = get_risk_level(probability)
    health_score = get_health_score(probability)
    
    # --- Explainable AI (SHAP) ---
    shap_explanation = {}
    try:
        clf = pipeline.named_steps["classifier"]
        scaler = pipeline.named_steps.get("scaler", None)
        
        # Transform data for SHAP if a scaler is used
        X_eval = scaler.transform(df) if scaler else df
        
        if model_name in ["Random Forest", "Decision Tree", "XGBoost", "LightGBM"]:
            explainer = shap.TreeExplainer(clf)
            shap_vals = explainer.shap_values(X_eval)
        else:
            # Fallback to KernelExplainer using saved subset
            bg_data = artifact.get("explainer_data")
            if bg_data is not None:
                explainer = shap.KernelExplainer(clf.predict_proba, bg_data)
                shap_vals = explainer.shap_values(X_eval)[positive_index]
            else:
                shap_vals = None
                
        if shap_vals is not None:
            # SHAP returns a list for multiclass (or binary in some models like RF)
            vals = shap_vals[0] if isinstance(shap_vals, list) else shap_vals[0]
            
            # Map features to their SHAP impacts
            feature_impacts = []
            for i, feature in enumerate(FEATURES):
                impact = float(vals[i])
                if abs(impact) > 0.01: # Filter negligible contributions
                    feature_impacts.append({
                        "feature": feature,
                        "value": float(df[feature].iloc[0]),
                        "impact": impact
                    })
                    
            # Sort by absolute impact magnitude
            feature_impacts.sort(key=lambda x: abs(x["impact"]), reverse=True)
            shap_explanation = {"top_factors": feature_impacts[:5]} # Top 5 factors
            
    except Exception as e:
        print(f"Failed to generate SHAP explanation: {e}")
        shap_explanation = {"error": "Explanation unavailable"}

    return {
        "positive": prediction,
        "probability": probability,
        "risk_level": risk_level,
        "health_score": health_score,
        "shap_explanation": json.dumps(shap_explanation),
        "model_name": model_name,
    }


def get_model_metrics():
    """Returns the performance metrics of the currently loaded model."""
    path = Path(settings.ML_METRICS_PATH)
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}