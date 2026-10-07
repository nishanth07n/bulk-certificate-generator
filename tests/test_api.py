import os

from fastapi.testclient import TestClient

from app.main import app
from app.generator import generate_certificate


client = TestClient(app)


def test_create_job():
    response = client.post(
        "/jobs",
        json={
            "course_name": "Python Course",
            "organization": "Test Organization",
            "recipients": [
                {
                    "name": "Rahul",
                    "email": "rahul@gmail.com"
                }
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "job_id" in data
    assert data["total"] == 1


def test_invalid_email():
    response = client.post(
        "/jobs",
        json={
            "course_name": "Python Course",
            "organization": "Test Organization",
            "recipients": [
                {
                    "name": "Rahul",
                    "email": "invalid-email"
                }
            ]
        }
    )

    assert response.status_code == 422


def test_empty_recipients():
    response = client.post(
        "/jobs",
        json={
            "course_name": "Python Course",
            "organization": "Test Organization",
            "recipients": []
        }
    )

    assert response.status_code == 400


def test_certificate_generation():
    certificate_id = "test-certificate"

    file_path = generate_certificate(
        certificate_id,
        "Test User",
        "Python Course",
        "Test Organization"
    )

    assert os.path.exists(file_path)

    os.remove(file_path)


def test_job_status():
    response = client.post(
        "/jobs",
        json={
            "course_name": "Python Course",
            "organization": "Test Organization",
            "recipients": [
                {
                    "name": "Test User",
                    "email": "test@gmail.com"
                }
            ]
        }
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    response = client.get(f"/jobs/{job_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert data["total"] == 1


def test_individual_certificate_failure(monkeypatch):
    def failing_generator(*args, **kwargs):
        raise Exception("Certificate generation failed")

    monkeypatch.setattr(
        "app.processor.generate_certificate",
        failing_generator
    )

    response = client.post(
        "/jobs",
        json={
            "course_name": "Python Course",
            "organization": "Test Organization",
            "recipients": [
                {
                    "name": "User One",
                    "email": "user1@gmail.com"
                }
            ]
        }
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    response = client.get(f"/jobs/{job_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["failed"] == 1
def test_retrieve_generated_certificate():

    response = client.post(
        "/jobs",
        json={
            "course_name": "Python Course",
            "organization": "Test Organization",
            "recipients": [
                {
                    "name": "Certificate User",
                    "email": "certificate@gmail.com"
                }
            ]
        }
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    response = client.get(f"/jobs/{job_id}/certificates")

    assert response.status_code == 200

    certificates = response.json()

    assert len(certificates) == 1

    certificate_id = certificates[0]["certificate_id"]

    response = client.get(
        f"/certificates/{certificate_id}"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"