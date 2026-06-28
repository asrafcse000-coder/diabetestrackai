from flask import Flask, render_template, request, jsonify, send_file
from model_loader import DiabetesModel
from datetime import datetime
import os
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image as RLImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

app = Flask(__name__)

# Initialize model loader
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "tuned_random_forest_model.joblib")
diabetes_predictor = DiabetesModel(MODEL_PATH)

# Store prediction data in session for PDF generation
prediction_cache = {}

# ============== ROUTES ==============

@app.route('/')
def home():
    """Landing page / Dashboard"""
    return render_template('home.html')

@app.route('/assessment')
def assessment():
    """Assessment form page"""
    return render_template('assessment.html')

@app.route('/about')
def about():
    """About page - explains the ML model"""
    return render_template('about.html')

@app.route('/contact')
def contact():
    """Contact/Feedback page"""
    return render_template('contact.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Process form submission and generate prediction.
    Collects patient metadata and ML input, returns enhanced results page.
    """
    try:
        # Collect patient metadata
        patient_name = request.form.get('patient_name', 'Unknown')
        age_value = request.form.get('age', '')
        gender = request.form.get('gender', '')
        assessment_date = request.form.get('assessment_date', datetime.now().strftime('%Y-%m-%d'))
        ref_doctor = request.form.get('ref_doctor', 'N/A')
        
        # Collect medical data
        form_data = request.form.to_dict()
        
        # Preprocess and predict
        processed_df = diabetes_predictor.preprocess_input(form_data)
        prediction, probability = diabetes_predictor.predict(processed_df)
        
        # Map prediction to text
        result_text = "Diabetic" if prediction == 1 else "Non-Diabetic"
        risk_level = "High Risk" if probability >= 75 else "Moderate Risk" if probability >= 50 else "Low Risk"
        
        # Calculate health metrics for comparison
        health_metrics = {
            'glucose': {
                'value': float(form_data.get('glucose', 0)),
                'normal_max': 100,
                'fasting_max': 125
            },
            'bmi': {
                'value': float(form_data.get('bmi', 0)),
                'normal_max': 25,
                'overweight_max': 30
            },
            'hba1c': {
                'value': float(form_data.get('hba1c', 0)),
                'normal_max': 5.7,
                'prediabetic_max': 6.4
            }
        }
        
        # Cache prediction data for PDF generation
        prediction_id = f"pred_{int(datetime.now().timestamp() * 1000)}"
        prediction_cache[prediction_id] = {
            'patient_name': patient_name,
            'age': age_value,
            'gender': gender,
            'assessment_date': assessment_date,
            'ref_doctor': ref_doctor,
            'form_data': form_data,
            'prediction': result_text,
            'probability': probability,
            'risk_level': risk_level,
            'health_metrics': health_metrics
        }
        
        return render_template('result.html', 
                               prediction_id=prediction_id,
                               patient_name=patient_name,
                               age=age_value,
                               gender=gender,
                               assessment_date=assessment_date,
                               ref_doctor=ref_doctor,
                               prediction=result_text,
                               probability=probability,
                               risk_level=risk_level,
                               data=form_data,
                               health_metrics=health_metrics)
    
    except Exception as e:
        return f"An error occurred: {str(e)}", 400

@app.route('/download-pdf/<prediction_id>')
def download_pdf(prediction_id):
    """Generate and download PDF report"""
    if prediction_id not in prediction_cache:
        return "Prediction not found", 404
    
    pred_data = prediction_cache[prediction_id]
    
    # Create PDF in memory
    pdf_buffer = io.BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                            rightMargin=0.5*inch, leftMargin=0.5*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#374151'),
        spaceAfter=4
    )
    
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#111827'),
        spaceAfter=4
    )
    
    # Build PDF content
    content = []
    
    # Header with logo placeholder and title
    header_data = [
        [Paragraph("🏥", heading_style), 
         Paragraph("<b>Diabetes Track AI</b><br/>Clinical Assessment Report", title_style)]
    ]
    header_table = Table(header_data, colWidths=[0.8*inch, 5.7*inch])
    header_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (0, 0), 28),
    ]))
    content.append(header_table)
    content.append(Spacer(1, 0.3*inch))
    
    # Report date
    content.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %H:%M')}", normal_style))
    content.append(Spacer(1, 0.15*inch))
    
    # Patient Information Section
    content.append(Paragraph("PATIENT INFORMATION", heading_style))
    patient_info = [
        ["Patient Name:", pred_data['patient_name']],
        ["Age:", pred_data['age']],
        ["Gender:", pred_data['gender']],
        ["Assessment Date:", pred_data['assessment_date']],
        ["Referring Physician:", pred_data['ref_doctor']],
    ]
    patient_table = Table(patient_info, colWidths=[2.0*inch, 4.5*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e5e7eb')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    content.append(patient_table)
    content.append(Spacer(1, 0.2*inch))
    
    # Clinical Measurements Section
    content.append(Paragraph("CLINICAL MEASUREMENTS", heading_style))
    measurements = [
        ["Metric", "Value", "Normal Range", "Status"],
        ["Blood Glucose (mg/dL)", 
         str(pred_data['form_data'].get('glucose', 'N/A')),
         "70-100 (fasting)",
         "⚠️ Check" if float(pred_data['form_data'].get('glucose', 0)) > 100 else "✓ Normal"],
        ["BMI (kg/m²)", 
         str(pred_data['form_data'].get('bmi', 'N/A')),
         "18.5-24.9",
         "⚠️ Check" if float(pred_data['form_data'].get('bmi', 0)) > 25 else "✓ Normal"],
        ["HbA1c Level (%)", 
         str(pred_data['form_data'].get('hba1c', 'N/A')),
         "< 5.7",
         "⚠️ Check" if float(pred_data['form_data'].get('hba1c', 0)) > 5.7 else "✓ Normal"],
    ]
    
    metrics_table = Table(measurements, colWidths=[1.5*inch, 1.2*inch, 1.5*inch, 1.3*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    content.append(metrics_table)
    content.append(Spacer(1, 0.2*inch))
    
    # Prediction Result Section
    content.append(Paragraph("PREDICTION RESULT", heading_style))
    result_color = colors.HexColor('#dc2626') if pred_data['prediction'] == 'Diabetic' else colors.HexColor('#16a34a')
    result_data = [
        [Paragraph(f"<font color='#ffffff'><b>DIAGNOSIS:</b></font>", normal_style),
         Paragraph(f"<font color='#ffffff'><b>{pred_data['prediction'].upper()}</b></font>", normal_style)],
        [Paragraph(f"<b>Risk Level:</b>", label_style),
         Paragraph(f"<b>{pred_data['risk_level']}</b>", label_style)],
        [Paragraph(f"<b>Confidence:</b>", label_style),
         Paragraph(f"<b>{pred_data['probability']}%</b>", label_style)],
    ]
    
    result_table = Table(result_data, colWidths=[2.5*inch, 4.0*inch])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), result_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f3f4f6')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    content.append(result_table)
    content.append(Spacer(1, 0.2*inch))
    
    # Medical Disclaimer
    content.append(Paragraph("DISCLAIMER", heading_style))
    disclaimer_text = (
        "This report is generated by the Diabetes Track AI machine learning model for educational and research purposes only. "
        "The predictions provided are based on the input clinical parameters and statistical patterns learned from training data. "
        "This is NOT a substitute for professional medical diagnosis, treatment, or advice. "
        "Always consult with a qualified healthcare professional for accurate diagnosis and treatment recommendations. "
        "The application developers assume no liability for the accuracy or use of these predictions."
    )
    content.append(Paragraph(disclaimer_text, label_style))
    content.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_text = "© 2026 Diabetes Track AI. All rights reserved. For educational purposes only."
    content.append(Paragraph(footer_text, label_style))
    
    # Build PDF
    pdf.build(content)
    pdf_buffer.seek(0)
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'DiabetesTrackAI_Report_{pred_data["patient_name"]}.pdf'
    )

@app.route('/submit-contact', methods=['POST'])
def submit_contact():
    """Handle contact form submission"""
    try:
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        message = request.form.get('message', '')
        
        # In production, you would save this to a database or send an email
        # For now, we'll just return success
        print(f"Contact: {name} ({email}) - {message}")
        
        return jsonify({'success': True, 'message': 'Thank you for reaching out!'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# ============== ERROR HANDLERS ==============

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
