"""
Models for the prediction application.
"""
from django.conf import settings
from django.db import models

class PredictionHistory(models.Model):
    """Stores individual patient predictions and their outcomes."""
    RISK_CHOICES = (
        ("low", "Low Risk"),
        ("moderate", "Moderate Risk"),
        ("high", "High Risk"),
        ("critical", "Critical Risk"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="predictions"
    )
    
    # Clinical Features
    age = models.PositiveSmallIntegerField()
    sex = models.PositiveSmallIntegerField(help_text="1: Male, 0: Female")
    cp = models.PositiveSmallIntegerField(help_text="Chest Pain Type (0-3)")
    trestbps = models.PositiveSmallIntegerField(help_text="Resting Blood Pressure (mm Hg)")
    chol = models.PositiveSmallIntegerField(help_text="Serum Cholestoral (mg/dl)")
    fbs = models.PositiveSmallIntegerField(help_text="Fasting Blood Sugar > 120 mg/dl (1=true, 0=false)")
    restecg = models.PositiveSmallIntegerField(help_text="Resting Electrocardiographic Results (0-2)")
    thalach = models.PositiveSmallIntegerField(help_text="Maximum Heart Rate Achieved")
    exang = models.PositiveSmallIntegerField(help_text="Exercise Induced Angina (1=yes, 0=no)")
    oldpeak = models.FloatField(help_text="ST depression induced by exercise relative to rest")
    slope = models.PositiveSmallIntegerField(help_text="Slope of the peak exercise ST segment (0-2)")
    ca = models.PositiveSmallIntegerField(help_text="Number of major vessels (0-3) colored by flourosopy")
    thal = models.PositiveSmallIntegerField(help_text="Thalassemia (0=normal, 1=fixed defect, 2=reversable defect)")
    
    # Model Output
    predicted_disease = models.BooleanField(help_text="True if disease predicted, False otherwise")
    risk_probability = models.FloatField(help_text="Probability of having heart disease (0.0 to 1.0)")
    risk_level = models.CharField(max_length=15, choices=RISK_CHOICES)
    model_name = models.CharField(max_length=80, help_text="Name of the model used for prediction")
    
    # CardioAI Advanced Fields
    health_score = models.IntegerField(default=100, help_text="Overall Health Score out of 100")
    shap_explanation = models.TextField(blank=True, help_text="JSON string of top contributing features")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Prediction History"
        verbose_name_plural = "Prediction Histories"

    @property
    def risk_percentage(self):
        """Returns risk probability as a percentage."""
        return self.risk_probability * 100
        
    def get_shap_dict(self):
        """Returns the parsed SHAP explanation."""
        import json
        if not self.shap_explanation:
            return {}
        try:
            return json.loads(self.shap_explanation)
        except Exception:
            return {}

    def __str__(self):
        return "Prediction for {} on {}".format(
            self.user.username, self.created_at.strftime("%Y-%m-%d %H:%M")
        )