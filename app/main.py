from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models import Job, Certificate
from app.schemas import JobRequest
from app.processor import process_job


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bulk Certificate Generator")


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {
        "message": "Bulk Certificate Generator API"
    }


@app.post("/jobs")
def create_job(
    request: JobRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    if not request.recipients:
        raise HTTPException(
            status_code=400,
            detail="At least one recipient is required"
        )

    job = Job(
        status="queued",
        total=len(request.recipients)
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    recipients = [
        {
            "name": r.name,
            "email": r.email
        }
        for r in request.recipients
    ]

    background_tasks.add_task(
        process_job,
        job.id,
        recipients,
        request.course_name,
        request.organization
    )

    return {
        "job_id": job.id,
        "status": job.status,
        "total": job.total
    }


@app.get("/jobs/{job_id}")
def get_job(
    job_id: str,
    db: Session = Depends(get_db)
):

    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    pending = job.total - job.successful - job.failed

    return {
        "job_id": job.id,
        "status": job.status,
        "total": job.total,
        "successful": job.successful,
        "failed": job.failed,
        "pending": pending
    }


@app.get("/jobs/{job_id}/certificates")
def get_certificates(
    job_id: str,
    db: Session = Depends(get_db)
):

    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    certificates = (
        db.query(Certificate)
        .filter(Certificate.job_id == job_id)
        .all()
    )

    return [
        {
            "certificate_id": certificate.id,
            "recipient_name": certificate.recipient_name,
            "recipient_email": certificate.recipient_email,
            "status": certificate.status,
            "file_path": certificate.file_path,
            "error": certificate.error_message
        }
        for certificate in certificates
    ]


@app.get("/certificates/{certificate_id}")
def download_certificate(
    certificate_id: str,
    db: Session = Depends(get_db)
):

    certificate = (
        db.query(Certificate)
        .filter(Certificate.id == certificate_id)
        .first()
    )

    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found"
        )

    if certificate.status != "success":
        raise HTTPException(
            status_code=400,
            detail="Certificate was not generated successfully"
        )

    return FileResponse(
        certificate.file_path,
        media_type="application/pdf",
        filename=f"{certificate.recipient_name}.pdf"
    )