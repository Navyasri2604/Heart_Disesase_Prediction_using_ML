"""
Admin configuration for the prediction application.
"""
import csv
from django.contrib import admin
from django.http import HttpResponse

from .models import PredictionHistory


def export_as_csv(modeladmin, request, queryset):
    """Admin action to export selected predictions as CSV."""
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="predictions_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        "ID", "User", "Date", "Age", "Sex", "Outcome", "Probability", "Risk Level"
    ])
    
    for obj in queryset:
        writer.writerow([
            obj.pk, obj.user.username, obj.created_at.strftime("%Y-%m-%d %H:%M"),
            obj.age, "M" if obj.sex == 1 else "F", 
            "Positive" if obj.predicted_disease else "Negative",
            "{:.2f}".format(obj.risk_probability), obj.risk_level
        ])
        
    return response
export_as_csv.short_description = "Export Selected as CSV"


@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "age", "predicted_disease", "risk_level", "created_at")
    list_filter = ("predicted_disease", "risk_level", "created_at", "sex")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "risk_probability", "model_name")
    actions = [export_as_csv]
    
    fieldsets = (
        ("Patient Info", {
            "fields": ("user", "age", "sex")
        }),
        ("Clinical Inputs", {
            "fields": ("cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal")
        }),
        ("Model Output", {
            "fields": ("predicted_disease", "risk_level", "risk_probability", "model_name", "created_at")
        }),
    )