"""
Views for the dashboard application.
"""
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import render, redirect

from prediction.ml_service import get_model_metrics
from prediction.models import PredictionHistory


def landing(request):
    """Renders the CardioAI public landing page."""
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    return render(request, "landing.html")


@login_required
def home(request):
    """Renders the CardioAI advanced analytics dashboard."""
    total_assessments = PredictionHistory.objects.count()

    risk_counts = PredictionHistory.objects.values('risk_level').annotate(count=Count('id'))
    risk_data = {item['risk_level']: item['count'] for item in risk_counts}

    low_risk = risk_data.get('low', 0)
    moderate_risk = risk_data.get('moderate', 0)
    high_risk = risk_data.get('high', 0)
    critical_risk = risk_data.get('critical', 0)

    metrics = get_model_metrics()
    model_name = metrics.get("selected_model", "N/A")
    accuracy = metrics.get("metrics", {}).get("accuracy", 0.0) * 100

    recent = PredictionHistory.objects.order_by("-created_at")[:5]

    chart_data = {
        "risk_distribution": [low_risk, moderate_risk, high_risk, critical_risk],
        "risk_labels": ["Low", "Moderate", "High", "Critical"],
        "accuracy": accuracy
    }

    context = {
        "total": total_assessments,
        "low_risk": low_risk,
        "moderate_risk": moderate_risk,
        "high_risk": high_risk,
        "critical_risk": critical_risk,
        "ml_accuracy": accuracy,
        "model_name": model_name,
        "recent_predictions": recent,
        "chart_data_json": json.dumps(chart_data)
    }
    return render(request, "dashboard/home.html", context)


@login_required
def analytics(request):
    """Visual analytics page with dataset insights."""
    # Feature importance data for the analytics page (based on typical Cleveland dataset SHAP values)
    feature_importance = [
        {"name": "Number of Major Vessels (ca)", "importance": "High", "width": 95},
        {"name": "Thalassemia Type (thal)", "importance": "High", "width": 88},
        {"name": "Chest Pain Type (cp)", "importance": "High", "width": 82},
        {"name": "ST Depression (oldpeak)", "importance": "Medium", "width": 72},
        {"name": "Exercise Angina (exang)", "importance": "Medium", "width": 65},
        {"name": "Max Heart Rate (thalach)", "importance": "Medium", "width": 60},
        {"name": "ST Slope (slope)", "importance": "Medium", "width": 54},
        {"name": "Age", "importance": "Low", "width": 42},
        {"name": "Resting Blood Pressure", "importance": "Low", "width": 35},
        {"name": "Cholesterol (chol)", "importance": "Low", "width": 30},
    ]
    return render(request, "dashboard/analytics.html", {"feature_importance": feature_importance})


@login_required
def model_performance(request):
    """Model performance dashboard showing all ML model comparisons."""
    metrics = get_model_metrics()
    selected_model = metrics.get("selected_model", "Unknown")
    all_models_data = metrics.get("all_models_comparison", {})

    all_models = []
    model_names = []
    accuracies = []
    f1_scores = []
    recalls = []

    for name, m in all_models_data.items():
        acc = round(m.get("accuracy", 0) * 100, 1)
        prec = round(m.get("precision", 0) * 100, 1)
        rec = round(m.get("recall", 0) * 100, 1)
        f1 = round(m.get("f1_score", 0) * 100, 1)
        cv = round(m.get("cv_accuracy_mean", 0) * 100, 1)
        all_models.append({
            "name": name,
            "accuracy": acc,
            "accuracy_pct": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "cv_accuracy": cv,
        })
        model_names.append(name)
        accuracies.append(acc)
        f1_scores.append(f1)
        recalls.append(rec)

    # Sort by CV accuracy descending
    all_models.sort(key=lambda x: x["cv_accuracy"], reverse=True)

    best = metrics.get("metrics", {})
    best_accuracy = round(best.get("accuracy", 0) * 100, 1)
    best_precision = round(best.get("precision", 0) * 100, 1)
    best_recall = round(best.get("recall", 0) * 100, 1)
    best_f1 = round(best.get("f1_score", 0) * 100, 1)
    best_cv = round(best.get("cv_accuracy_mean", 0) * 100, 1)

    context = {
        "selected_model": selected_model,
        "all_models": all_models,
        "best_accuracy": best_accuracy,
        "best_precision": best_precision,
        "best_recall": best_recall,
        "best_f1": best_f1,
        "best_cv": best_cv,
        "model_names_json": json.dumps(model_names),
        "accuracies_json": json.dumps(accuracies),
        "f1_json": json.dumps(f1_scores),
        "recalls_json": json.dumps(recalls),
    }
    return render(request, "dashboard/model_performance.html", context)


@login_required
def bmi_calculator(request):
    """BMI Calculator and Heart Health Score tool."""
    return render(request, "dashboard/bmi_calculator.html")