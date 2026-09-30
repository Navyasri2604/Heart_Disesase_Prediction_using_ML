from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from prediction.forms import PatientPredictionForm
from prediction.models import Prediction

VALID_DATA = {
    "age": 54, "sex": 1, "cp": 1, "trestbps": 130, "chol": 246, "fbs": 0,
    "restecg": 0, "thalach": 150, "exang": 0, "oldpeak": 1.2, "slope": 1, "ca": 0, "thal": 3,
}


class PredictionFormTests(TestCase):
    def test_accepts_valid_uci_feature_values(self):
        form = PatientPredictionForm(data=VALID_DATA)
        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_out_of_range_measurements(self):
        form = PatientPredictionForm(data={**VALID_DATA, "age": 12, "chol": 1000})
        self.assertFalse(form.is_valid())
        self.assertIn("age", form.errors)
        self.assertIn("chol", form.errors)

    def test_uses_original_uci_thal_codes(self):
        form = PatientPredictionForm(data={**VALID_DATA, "thal": 4})
        self.assertFalse(form.is_valid())
        self.assertIn("thal", form.errors)

    def test_rejects_zero_based_chest_pain_and_slope_codes(self):
        form = PatientPredictionForm(data={**VALID_DATA, "cp": 0, "slope": 0})
        self.assertFalse(form.is_valid())
        self.assertIn("cp", form.errors)
        self.assertIn("slope", form.errors)


class PredictionViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="clinician", password="test-password-8271")
        self.client.force_login(self.user)

    def test_prediction_is_saved_and_result_shown(self):
        result = {"positive": True, "probability": 0.82, "risk_level": "high", "model_name": "Test model"}
        with patch("prediction.views.predict", return_value=result):
            response = self.client.post(reverse("prediction:create"), VALID_DATA)
        record = Prediction.objects.get(user=self.user)
        self.assertRedirects(response, reverse("prediction:result", args=[record.pk]))
        self.assertTrue(record.predicted_disease)
        self.assertEqual(record.risk_level, "high")

    def test_users_cannot_open_another_users_result_or_report(self):
        other = get_user_model().objects.create_user(username="another", password="test-password-8271")
        record = Prediction.objects.create(user=other, **VALID_DATA, predicted_disease=False,
                                           risk_probability=0.12, risk_level="low", model_name="Test")
        self.assertEqual(self.client.get(reverse("prediction:result", args=[record.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("prediction:report", args=[record.pk])).status_code, 404)

    def test_report_is_downloadable_csv(self):
        record = Prediction.objects.create(user=self.user, **VALID_DATA, predicted_disease=False,
                                           risk_probability=0.12, risk_level="low", model_name="Test")
        response = self.client.get(reverse("prediction:report", args=[record.pk]))
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn(b"not a medical diagnosis", response.content)

    def test_result_page_shows_risk_percentage_and_recommendation(self):
        record = Prediction.objects.create(user=self.user, **VALID_DATA, predicted_disease=True,
                                           risk_probability=0.82, risk_level="high", model_name="Test")
        response = self.client.get(reverse("prediction:result", args=[record.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "82<small>%</small>")
        self.assertContains(response, "licensed healthcare professional")

    def test_prediction_form_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("prediction:create"))
        self.assertRedirects(response, "{}?next={}".format(reverse("accounts:login"), reverse("prediction:create")))