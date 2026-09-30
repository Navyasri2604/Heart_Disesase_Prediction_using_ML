"""
URLs for the dashboard application.
"""
from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("dashboard/", views.home, name="home"),
    path("dashboard/analytics/", views.analytics, name="analytics"),
    path("dashboard/model-performance/", views.model_performance, name="model_performance"),
    path("dashboard/bmi-calculator/", views.bmi_calculator, name="bmi_calculator"),
]