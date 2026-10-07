from pydantic import BaseModel, EmailStr
from typing import List


class Recipient(BaseModel):
    name: str
    email: EmailStr


class JobRequest(BaseModel):
    course_name: str
    organization: str
    recipients: List[Recipient]