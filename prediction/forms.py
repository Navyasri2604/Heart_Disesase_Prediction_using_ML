"""
Forms for the prediction application.
"""
from django import forms


class PatientPredictionForm(forms.Form):
    """Form to collect patient clinical data for heart disease prediction."""
    CHOICES = {
        "sex": ((0, "Female"), (1, "Male")),
        "cp": (
            (0, "Typical Angina (0)"), 
            (1, "Atypical Angina (1)"), 
            (2, "Non-anginal Pain (2)"), 
            (3, "Asymptomatic (3)")
        ),
        "fbs": ((0, "False (< 120 mg/dl)"), (1, "True (> 120 mg/dl)")),
        "restecg": (
            (0, "Normal (0)"), 
            (1, "ST-T wave abnormality (1)"), 
            (2, "Left ventricular hypertrophy (2)")
        ),
        "exang": ((0, "No (0)"), (1, "Yes (1)")),
        "slope": (
            (0, "Upsloping (0)"), 
            (1, "Flat (1)"), 
            (2, "Downsloping (2)")
        ),
        "ca": ((0, "0"), (1, "1"), (2, "2"), (3, "3"), (4, "4")),
        "thal": ((0, "Normal (0)"), (1, "Fixed Defect (1)"), (2, "Reversable Defect (2)"), (3, "Other (3)")),
    }

    age = forms.IntegerField(
        min_value=1, max_value=120, label="Age", help_text="Patient's age in years",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    sex = forms.TypedChoiceField(
        choices=CHOICES["sex"], coerce=int, label="Gender",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    cp = forms.TypedChoiceField(
        choices=CHOICES["cp"], coerce=int, label="Chest Pain Type",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    trestbps = forms.IntegerField(
        min_value=50, max_value=250, label="Resting Blood Pressure", help_text="In mm Hg on admission",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    chol = forms.IntegerField(
        min_value=50, max_value=600, label="Serum Cholestoral", help_text="In mg/dl",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    fbs = forms.TypedChoiceField(
        choices=CHOICES["fbs"], coerce=int, label="Fasting Blood Sugar",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    restecg = forms.TypedChoiceField(
        choices=CHOICES["restecg"], coerce=int, label="Resting ECG Results",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    thalach = forms.IntegerField(
        min_value=50, max_value=250, label="Maximum Heart Rate Achieved", help_text="In beats per minute",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )
    exang = forms.TypedChoiceField(
        choices=CHOICES["exang"], coerce=int, label="Exercise Induced Angina",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    oldpeak = forms.FloatField(
        min_value=0.0, max_value=10.0, label="ST Depression", help_text="Induced by exercise relative to rest",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.1"})
    )
    slope = forms.TypedChoiceField(
        choices=CHOICES["slope"], coerce=int, label="Slope of Peak Exercise ST Segment",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    ca = forms.TypedChoiceField(
        choices=CHOICES["ca"], coerce=int, label="Number of Major Vessels", help_text="Colored by flourosopy",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    thal = forms.TypedChoiceField(
        choices=CHOICES["thal"], coerce=int, label="Thalassemia",
        widget=forms.Select(attrs={"class": "form-select"})
    )