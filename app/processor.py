from app.database import SessionLocal
from app.models import Job, Certificate
from app.generator import generate_certificate


def process_job(job_id, recipients, course_name, organization):

    db = SessionLocal()

    job = db.query(Job).filter(Job.id == job_id).first()

    job.status = "processing"
    db.commit()

    for recipient in recipients:

        certificate = Certificate(
            job_id=job_id,
            recipient_name=recipient["name"],
            recipient_email=recipient["email"],
            course_name=course_name,
            status="processing"
        )

        db.add(certificate)
        db.commit()

        try:

            file_path = generate_certificate(
                certificate.id,
                recipient["name"],
                course_name,
                organization
            )

            certificate.status = "success"
            certificate.file_path = file_path

            job.successful += 1

        except Exception as e:

            certificate.status = "failed"
            certificate.error_message = str(e)

            job.failed += 1

        db.commit()

    job.status = "completed"

    db.commit()
    db.close()