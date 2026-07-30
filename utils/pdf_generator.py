"""
pdf_generator.py
-----------------
Generates a professional Medical Report PDF from a completed prediction result.

Uses reportlab (pure-Python, no external system dependencies like
wkhtmltopdf) to keep this beginner-friendly and easy to install.

Used by the /download-report route in app.py.
"""

import io
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Brand colors matching the website's palette
PRIMARY_BLUE = colors.HexColor("#2563eb")
PRIMARY_TEAL = colors.HexColor("#0d9488")
DARK = colors.HexColor("#0f172a")
MUTED = colors.HexColor("#64748b")
WARN_BG = colors.HexColor("#fff7ed")
WARN_TEXT = colors.HexColor("#9a3412")


def generate_medical_report_pdf(result: dict) -> io.BytesIO:
    """
    Build a Medical Report PDF from a result dictionary (the same shape
    stored in session['result'] by app.py) and return it as an in-memory
    BytesIO buffer, ready to send with Flask's send_file().
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=18 * mm, bottomMargin=18 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", fontSize=20, textColor=DARK,
                               fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=2))
    styles.add(ParagraphStyle(name="ReportSubtitle", fontSize=10, textColor=MUTED,
                               alignment=TA_CENTER, spaceAfter=10))
    styles.add(ParagraphStyle(name="SectionHeading", fontSize=13, textColor=PRIMARY_BLUE,
                               fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6))
    styles.add(ParagraphStyle(name="BodyMuted", fontSize=10, textColor=DARK, leading=15))
    styles.add(ParagraphStyle(name="Disclaimer", fontSize=8.5, textColor=WARN_TEXT, leading=12))

    elements = []

    # ---------------- Header ----------------
    elements.append(Paragraph("MediPredict AI", styles["ReportTitle"]))
    elements.append(Paragraph("AI-Based Disease Prediction &amp; Healthcare Recommendation System",
                               styles["ReportSubtitle"]))
    elements.append(HRFlowable(width="100%", thickness=1.2, color=PRIMARY_TEAL, spaceAfter=10))
    elements.append(Paragraph("MEDICAL PREDICTION REPORT", styles["SectionHeading"]))

    # ---------------- Patient Info Table ----------------
    generated_at = datetime.now().strftime("%d %B %Y, %I:%M %p")
    patient_table_data = [
        ["Patient Name", result.get("patient_name", "N/A"), "Date & Time", generated_at],
        ["Age", str(result.get("age", "N/A")), "Gender", result.get("gender", "N/A")],
    ]
    patient_table = Table(patient_table_data, colWidths=[35 * mm, 55 * mm, 35 * mm, 55 * mm])
    patient_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 0), (-1, -1), DARK),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 10))

    # ---------------- Symptoms ----------------
    elements.append(Paragraph("Reported Symptoms", styles["SectionHeading"]))
    symptoms_text = ", ".join(result.get("selected_symptoms", []))
    elements.append(Paragraph(symptoms_text, styles["BodyMuted"]))

    # ---------------- Prediction Summary ----------------
    elements.append(Paragraph("Prediction Summary", styles["SectionHeading"]))
    confidence = result.get("confidence")
    confidence_str = f"{confidence}%" if confidence is not None else "N/A"

    summary_data = [
        ["Predicted Disease", result.get("disease", "N/A")],
        ["Confidence Score", confidence_str],
        ["Risk / Severity Level", result.get("risk_level", "N/A")],
        ["Recommended Specialist", result.get("specialist", "N/A")],
    ]
    summary_table = Table(summary_data, colWidths=[55 * mm, 125 * mm])
    summary_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, -1), DARK),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 6))

    # ---------------- Description ----------------
    if result.get("description"):
        elements.append(Paragraph("About This Condition", styles["SectionHeading"]))
        elements.append(Paragraph(result["description"], styles["BodyMuted"]))

    # ---------------- Helper for bullet sections ----------------
    def bullet_section(title, items):
        elements.append(Paragraph(title, styles["SectionHeading"]))
        for item in items or []:
            elements.append(Paragraph(f"&ndash;&nbsp;&nbsp;{item}", styles["BodyMuted"]))

    bullet_section("Possible Causes", result.get("causes"))
    bullet_section("Precautions", result.get("precautions"))
    bullet_section("Diet Recommendation", result.get("diet"))
    bullet_section("Exercise Recommendation", result.get("exercise"))

    # ---------------- Doctor Consultation Advice ----------------
    if result.get("when_to_consult"):
        elements.append(Paragraph("When to Consult a Doctor", styles["SectionHeading"]))
        elements.append(Paragraph(result["when_to_consult"], styles["BodyMuted"]))

    # ---------------- Hospital (Demo) ----------------
    elements.append(Paragraph("Suggested Facility (Demo)", styles["SectionHeading"]))
    elements.append(Paragraph(
        f"City Care Multi-Specialty Hospital (Demo) &mdash; Recommended Specialist: {result.get('specialist', 'General Physician')}",
        styles["BodyMuted"]
    ))

    # ---------------- Disclaimer ----------------
    elements.append(Spacer(1, 14))
    elements.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#fed7aa")))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "<b>AI Disclaimer:</b> This report is generated by an educational Machine Learning "
        "project (MediPredict AI) and is <b>not</b> a certified medical diagnosis. It is intended "
        "for academic demonstration only. Please consult a certified healthcare professional for "
        "any medical concerns, diagnosis, or treatment.",
        styles["Disclaimer"]
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
