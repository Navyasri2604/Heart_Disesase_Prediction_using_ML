"""
Views for the prediction application.
"""
import csv
import io
import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

from accounts.views import _log_activity
from .forms import PatientPredictionForm
from .ml_service import predict
from .models import PredictionHistory


def _get_visible_predictions(user):
    """Staff can see all, users can see only theirs."""
    if user.is_staff:
        return PredictionHistory.objects.all()
    return PredictionHistory.objects.filter(user=user)


@login_required
def create_prediction(request):
    """View to collect patient data and generate a prediction."""
    form = PatientPredictionForm(request.POST or None)
    
    if request.method == "POST" and form.is_valid():
        values = form.cleaned_data
        
        try:
            # Send data to ML service
            result = predict(values)
        except Exception as error:
            messages.error(request, f"Analysis Error: {str(error)}")
            _log_activity(request.user, "Prediction Error", str(error), request)
        else:
            # Save the record
            record = PredictionHistory.objects.create(
                user=request.user,
                **values,
                predicted_disease=result["positive"],
                risk_probability=result["probability"],
                risk_level=result["risk_level"],
                health_score=result["health_score"],
                shap_explanation=result["shap_explanation"],
                model_name=result["model_name"],
            )
            
            _log_activity(
                request.user, 
                "Created Prediction", 
                f"Risk: {record.risk_level.title()} | Score: {record.health_score}", 
                request
            )
            
            messages.success(request, "AI Assessment completed successfully.")
            return redirect("prediction:result", pk=record.pk)
            
    return render(request, "prediction/form.html", {"form": form})


@login_required
def result(request, pk):
    """View a specific prediction result."""
    record = get_object_or_404(_get_visible_predictions(request.user), pk=pk)
    
    # Process SHAP data for template
    shap_data = record.get_shap_dict()
    top_factors = shap_data.get("top_factors", [])
    
    # Format factors for display (map variable names to human readable)
    feature_names = {
        "age": "Patient Age", "sex": "Gender", "cp": "Chest Pain Type",
        "trestbps": "Resting BP", "chol": "Cholesterol", "fbs": "Fasting Blood Sugar",
        "restecg": "Resting ECG", "thalach": "Max Heart Rate", "exang": "Exercise Angina",
        "oldpeak": "ST Depression", "slope": "ST Slope", "ca": "Major Vessels", "thal": "Thalassemia"
    }
    
    for factor in top_factors:
        factor["friendly_name"] = feature_names.get(factor["feature"], factor["feature"])
        factor["direction"] = "increased" if factor["impact"] > 0 else "decreased"
        factor["color_class"] = "text-danger" if factor["impact"] > 0 else "text-success"
    
    return render(request, "prediction/result.html", {
        "record": record,
        "top_factors": top_factors
    })


@login_required
def history(request):
    """List prediction history."""
    query = request.GET.get("q", "")
    records = _get_visible_predictions(request.user)
    
    if query:
        query_lower = query.lower()
        if "critical" in query_lower:
            records = records.filter(risk_level="critical")
        elif "high" in query_lower:
            records = records.filter(risk_level="high")
        elif "moderate" in query_lower:
            records = records.filter(risk_level="moderate")
        elif "low" in query_lower:
            records = records.filter(risk_level="low")
        elif query.isdigit():
            records = records.filter(age=int(query))
            
    return render(request, "prediction/history.html", {"records": records, "query": query})


@login_required
def download_report(request, pk):
    """Generate and download a professional PDF report."""
    record = get_object_or_404(_get_visible_predictions(request.user), pk=pk)
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(name="TitleStyle", parent=styles["Heading1"], fontSize=22, textColor=colors.HexColor("#0F172A"), alignment=1, spaceAfter=20)
    subtitle_style = ParagraphStyle(name="SubTitleStyle", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#4F46E5"), spaceAfter=15)
    normal_style = styles["Normal"]
    
    elements = []
    
    # Header
    elements.append(Paragraph("<b>CardioAI</b> Diagnostic Report", title_style))
    elements.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    elements.append(Paragraph(f"<b>Assessment ID:</b> {record.pk}", normal_style))
    elements.append(Paragraph(f"<b>Provider:</b> {request.user.get_full_name() or request.user.username}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Result Summary
    elements.append(Paragraph("AI Assessment Summary", subtitle_style))
    risk_color = "#10B981" # Green
    if record.risk_level in ["high", "critical"]:
        risk_color = "#EF4444" # Red
    elif record.risk_level == "moderate":
        risk_color = "#F59E0B" # Orange
        
    summary_data = [
        ["Overall Health Score", f"{record.health_score}/100"],
        ["Disease Probability", f"{record.risk_percentage:.1f}%"],
        ["Risk Categorization", record.risk_level.upper()]
    ]
    t = Table(summary_data, colWidths=[200, 200])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#64748B")),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor(risk_color)),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.white)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # Explainable AI
    elements.append(Paragraph("Explainable AI (SHAP) Insights", subtitle_style))
    shap_data = record.get_shap_dict().get("top_factors", [])
    if shap_data:
        elements.append(Paragraph("The following clinical factors were the primary drivers of this prediction:", normal_style))
        elements.append(Spacer(1, 10))
        shap_table_data = [["Factor", "Patient Value", "AI Impact Direction"]]
        for factor in shap_data:
            direction = "Increased Risk" if factor["impact"] > 0 else "Decreased Risk"
            shap_table_data.append([factor["feature"].upper(), str(factor["value"]), direction])
            
        st = Table(shap_table_data, colWidths=[150, 100, 150])
        st.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(st)
    else:
        elements.append(Paragraph("Explainability details are not available for this record.", normal_style))
        
    elements.append(Spacer(1, 20))
    
    # Clinical Inputs
    elements.append(Paragraph("Patient Clinical Vitals", subtitle_style))
    vitals = [
        ["Age", str(record.age), "Max Heart Rate", str(record.thalach)],
        ["Gender", "Male" if record.sex == 1 else "Female", "Resting BP", str(record.trestbps)],
        ["Cholesterol", str(record.chol), "Fasting Blood Sugar", "> 120" if record.fbs == 1 else "< 120"],
    ]
    vt = Table(vitals, colWidths=[120, 80, 120, 80])
    vt.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor("#F1F5F9")),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(vt)
    
    # Disclaimer
    elements.append(Spacer(1, 40))
    disclaimer = """<font size=8 color="#64748B"><b>DISCLAIMER:</b> This report is generated by an Artificial Intelligence system for informational purposes only. It does not constitute a medical diagnosis. A licensed physician must evaluate these results in a clinical setting before initiating any treatment.</font>"""
    elements.append(Paragraph(disclaimer, normal_style))
    
    # Build PDF
    doc.build(elements)
    
    buffer.seek(0)
    _log_activity(request.user, "Downloaded PDF Report", f"Report ID: {record.pk}", request)
    return FileResponse(buffer, as_attachment=True, filename=f"CardioAI_Report_{record.pk}.pdf")


@login_required
def export_csv(request, pk):
    """Export a single prediction record as a CSV file."""
    record = get_object_or_404(_get_visible_predictions(request.user), pk=pk)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="CardioAI_Record_{record.pk}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Assessment ID", "Date", "Patient Age", "Gender",
        "Chest Pain Type", "Resting BP", "Cholesterol", "Fasting Blood Sugar",
        "Resting ECG", "Max Heart Rate", "Exercise Angina", "ST Depression",
        "ST Slope", "Major Vessels", "Thalassemia",
        "Predicted Disease", "Risk Probability (%)", "Risk Level", "Health Score", "Model Used"
    ])
    writer.writerow([
        record.pk,
        record.created_at.strftime("%Y-%m-%d %H:%M"),
        record.age,
        "Male" if record.sex == 1 else "Female",
        record.cp,
        record.trestbps,
        record.chol,
        ">120 mg/dl" if record.fbs == 1 else "<120 mg/dl",
        record.restecg,
        record.thalach,
        "Yes" if record.exang == 1 else "No",
        record.oldpeak,
        record.slope,
        record.ca,
        record.thal,
        "Yes" if record.predicted_disease else "No",
        f"{record.risk_percentage:.2f}",
        record.risk_level.upper(),
        record.health_score,
        record.model_name,
    ])

    _log_activity(request.user, "Exported CSV", f"Record ID: {record.pk}", request)
    return response