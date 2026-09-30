"""
URLs for the prediction application.
"""
from django.urls import path

from . import views

app_name = "prediction"

urlpatterns = [
    path("new/", views.create_prediction, name="create"),
    path("history/", views.history, name="history"),
    path("<int:pk>/", views.result, name="result"),
    path("<int:pk>/report/download/", views.download_report, name="report"),
    path("<int:pk>/export/csv/", views.export_csv, name="export_csv"),
]