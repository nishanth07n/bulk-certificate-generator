import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def generate_certificate(
    certificate_id,
    recipient_name,
    course_name,
    organization
):
    os.makedirs("generated", exist_ok=True)

    file_path = f"generated/{certificate_id}.pdf"

    c = canvas.Canvas(file_path, pagesize=A4)

    width, height = A4

    # Border
    c.rect(40, 40, width - 80, height - 80)

    # Title
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(
        width / 2,
        height - 150,
        "CERTIFICATE"
    )

    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(
        width / 2,
        height - 190,
        "OF COMPLETION"
    )

    # Text
    c.setFont("Helvetica", 14)
    c.drawCentredString(
        width / 2,
        height - 260,
        "This certificate is proudly presented to"
    )

    # Recipient
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(
        width / 2,
        height - 310,
        recipient_name
    )

    c.setFont("Helvetica", 14)
    c.drawCentredString(
        width / 2,
        height - 370,
        "for successfully completing"
    )

    # Course
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(
        width / 2,
        height - 410,
        course_name
    )

    # Organization
    c.setFont("Helvetica", 14)
    c.drawCentredString(
        width / 2,
        height - 470,
        organization
    )

    c.save()

    return file_path