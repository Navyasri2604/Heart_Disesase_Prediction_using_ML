from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from prediction.models import Prediction


class DashboardPageTests(TestCase):
    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_dashboard_renders_summary_and_analytics(self):
        user = get_user_model().objects.create_user(username="dashboard-user", password="Secure-Password-920!")
        self.client.force_login(user)
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Total assessments")
        self.assertContains(response, "Age &amp; screening outcome")
        self.assertContains(response, "Gender mix")
        self.assertContains(response, "Feature importance")

    def test_staff_dashboard_aggregates_all_accounts_and_can_open_records(self):
        owner = get_user_model().objects.create_user(username="record-owner", password="Secure-Password-920!")
        staff = get_user_model().objects.create_user(username="staff-user", password="Secure-Password-920!", is_staff=True)
        record = Prediction.objects.create(
            user=owner, age=60, sex=1, cp=1, trestbps=130, chol=250, fbs=0, restecg=0,
            thalach=140, exang=1, oldpeak=1.5, slope=2, ca=1, thal=3,
            predicted_disease=True, risk_probability=0.8, risk_level="high", model_name="Test",
        )
        self.client.force_login(staff)
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.context["total"], 1)
        self.assertEqual(response.context["positive"], 1)
        self.assertEqual(response.context["cholesterol_values"], [0, 0, 1])
        self.assertEqual(self.client.get(reverse("prediction:result", args=[record.pk])).status_code, 200)