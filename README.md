# Bulk Certificate Generator

A backend API for generating certificates in bulk for multiple recipients using a predefined certificate template.

The application accepts a single certificate generation request containing multiple recipients, processes the certificates in the background, tracks the generation status, and provides APIs to retrieve the generated certificates.

---

## 1. Features

- Create bulk certificate generation jobs
- Accept multiple recipients in a single request
- Validate recipient information
- Generate PDF certificates using a predefined template
- Process certificates in the background
- Track job progress
- Track successful and failed certificate generations
- Handle individual certificate failures without stopping the entire job
- Retrieve certificates belonging to a job
- Download generated certificates
- Automated tests using Pytest

---

## 2. Technology Stack

- **Python 3**
- **FastAPI** - REST API framework
- **SQLite** - Relational database
- **SQLAlchemy** - Database ORM
- **Pydantic** - Request validation
- **ReportLab** - PDF certificate generation
- **Pytest** - Automated testing

---

## 3. Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── generator.py
│   └── processor.py
│
├── generated/
│   └── Generated certificate PDFs
│
├── tests/
│   ├── __init__.py
│   └── test_api.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 4. Setup

### Step 1: Clone or download the project

Open the project folder in VS Code.

### Step 2: Create a virtual environment

```bash
python3 -m venv .venv
```

### Step 3: Activate the virtual environment

For macOS/Linux:

```bash
source .venv/bin/activate
```

For Windows:

```bash
.venv\Scripts\activate
```

### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Run the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The application will run at:

```text
http://127.0.0.1:8000
```

FastAPI Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

The Swagger interface can be used to test all API endpoints.

---

## 6. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/jobs` | Create a certificate generation job |
| GET | `/jobs/{job_id}` | Check job status and progress |
| GET | `/jobs/{job_id}/certificates` | List certificates for a job |
| GET | `/certificates/{certificate_id}` | Download a generated certificate |

---

## 7. Create a Generation Job

### Endpoint

```text
POST /jobs
```

### Request

Example:

```json
{
  "course_name": "Python Backend Development",
  "organization": "ABC Technologies",
  "recipients": [
    {
      "name": "Rahul Sharma",
      "email": "rahul@gmail.com"
    },
    {
      "name": "Priya Kumar",
      "email": "priya@gmail.com"
    },
    {
      "name": "John Doe",
      "email": "john@gmail.com"
    }
  ]
}
```

### Response

```json
{
  "job_id": "example-job-id",
  "status": "queued",
  "total": 3
}
```

The returned `job_id` is used to track the generation process.

---

## 8. Check Job Status

### Endpoint

```text
GET /jobs/{job_id}
```

Example:

```text
GET /jobs/example-job-id
```

### Response

```json
{
  "job_id": "example-job-id",
  "status": "completed",
  "total": 3,
  "successful": 3,
  "failed": 0,
  "pending": 0
}
```

### Status Values

A job can have the following statuses:

- `queued`
- `processing`
- `completed`

The response also provides:

- Total recipients
- Successful certificates
- Failed certificates
- Pending certificates

---

## 9. Retrieve Certificates for a Job

### Endpoint

```text
GET /jobs/{job_id}/certificates
```

Example:

```text
GET /jobs/example-job-id/certificates
```

Example response:

```json
[
  {
    "certificate_id": "certificate-id-1",
    "recipient_name": "Rahul Sharma",
    "recipient_email": "rahul@gmail.com",
    "status": "success",
    "file_path": "generated/certificate-id-1.pdf",
    "error": null
  },
  {
    "certificate_id": "certificate-id-2",
    "recipient_name": "Priya Kumar",
    "recipient_email": "priya@gmail.com",
    "status": "success",
    "file_path": "generated/certificate-id-2.pdf",
    "error": null
  }
]
```

This endpoint allows the client to identify which certificates were successfully generated and which ones failed.

---

## 10. Download a Certificate

### Endpoint

```text
GET /certificates/{certificate_id}
```

Example:

```text
GET /certificates/certificate-id-1
```

The API returns the generated PDF file.

Generated certificates are stored in:

```text
generated/
```

---

## 11. Validation

Recipient information is validated using Pydantic.

Each recipient must contain:

```json
{
  "name": "Recipient Name",
  "email": "recipient@example.com"
}
```

Invalid email addresses are rejected.

For example:

```json
{
  "name": "Rahul",
  "email": "invalid-email"
}
```

results in a validation error.

The application also rejects requests containing an empty recipient list.

---

## 12. Failure Handling

Each recipient is processed independently.

For example, if a job contains five recipients:

```text
Recipient 1 → Success
Recipient 2 → Success
Recipient 3 → Failed
Recipient 4 → Success
Recipient 5 → Success
```

The failure of Recipient 3 does not stop the other certificates from being generated.

The failed certificate is stored with:

- `status = failed`
- An error message

The job status will report:

```json
{
  "total": 5,
  "successful": 4,
  "failed": 1,
  "pending": 0
}
```

---

## 13. Bulk Processing Design

The application uses **FastAPI BackgroundTasks** for certificate generation.

When the client creates a job:

```text
Client
   |
   | POST /jobs
   ↓
FastAPI
   |
   | Create Job
   ↓
Return Job ID
   |
   ↓
Background Processing
   |
   ├── Generate Certificate 1
   ├── Generate Certificate 2
   ├── Generate Certificate 3
   └── ...
```

This prevents the client from having to wait for every certificate before receiving a response.

The client can use the returned `job_id` to check the progress using:

```text
GET /jobs/{job_id}
```

For a production-scale application with very large workloads, a dedicated task queue such as Celery with Redis could be used instead.

---

## 14. Certificate Generation

A single predefined certificate template is used.

The generated certificate contains recipient-specific information including:

- Recipient name
- Course name
- Organization

ReportLab is used to generate the certificate as a PDF.

Example:

```text
CERTIFICATE

OF COMPLETION

This certificate is proudly presented to

Rahul Sharma

for successfully completing

Python Backend Development

ABC Technologies
```

---

## 15. Database Design

SQLite is used as the relational database.

### Jobs Table

The `jobs` table stores information about the overall generation request.

Important fields include:

```text
id
status
total
successful
failed
created_at
```

### Certificates Table

The `certificates` table stores information about individual certificates.

Important fields include:

```text
id
job_id
recipient_name
recipient_email
course_name
status
file_path
error_message
created_at
```

The `job_id` connects each certificate to its generation job.

---

## 16. Running Tests

The project uses Pytest.

Run:

```bash
pytest -v
```

The test suite covers:

1. Creating a generation job
2. Invalid recipient email validation
3. Empty recipient validation
4. Certificate PDF generation
5. Job status/progress
6. Individual certificate failure handling
7. Retrieving generated certificates

Expected result:

```text
7 passed
```

---

## 17. Design Decisions

### FastAPI

FastAPI was selected because it provides:

- Simple REST API development
- Automatic request validation
- Automatic Swagger documentation
- Good support for background tasks

### SQLite

SQLite was selected because it is a lightweight relational database that requires no separate database server and is sufficient for this assignment.

For production, PostgreSQL would be a better choice.

### Background Processing

Certificate generation is performed using FastAPI BackgroundTasks so that the API can return a job ID without waiting for all certificates to finish generating.

### Individual Failure Handling

Each certificate is processed independently using exception handling. A failure in one certificate does not stop the remaining certificates.

### ReportLab

ReportLab was selected because it provides a simple way to generate PDF certificates programmatically using a predefined layout.

---

## 18. Possible Production Improvements

For a larger production system, the following improvements could be considered:

- PostgreSQL instead of SQLite
- Celery/Redis or another task queue
- Cloud storage for generated certificates
- Authentication and authorization
- Rate limiting
- More detailed logging
- Certificate expiration/cleanup
- Email delivery of generated certificates

These features are not required for the current assignment.

---

## 19. Quick Start

```bash
python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

Create a job using:

```text
POST /jobs
```

Check progress using:

```text
GET /jobs/{job_id}
```

List certificates using:

```text
GET /jobs/{job_id}/certificates
```

Download a certificate using:

```text
GET /certificates/{certificate_id}
```

Run tests using:

```bash
pytest -v
```

Expected:

```text
7 passed
```