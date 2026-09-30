from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    student_id: int
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    intent: Literal[
        "CHECK_ELIGIBILITY",
        "LIST_SCHOLARSHIPS",
        "REQUIRED_DOCUMENTS",
        "APPLICATION_STATUS",
        "DISBURSEMENT",
        "STATISTICS",
        "UNKNOWN",
    ]
    response: str


class StudentCreate(BaseModel):
    name: str
    category: str
    state: str
    income: float
    education_level: str
    course: str


class StudentResponse(StudentCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ScholarshipResponse(BaseModel):
    name: str
    scheme: str
    category: str | None = None
    max_income: float | None = None
    education_level: str | None = None
    description: str | None = None
    id: int

    model_config = ConfigDict(from_attributes=True)


class ScholarshipStatisticsResponse(BaseModel):
    id: int
    financial_year: str
    scheme: str
    fund_released_crore: float
    beneficiaries: int
    source: str

    model_config = ConfigDict(from_attributes=True)


class StudentDocumentResponse(BaseModel):
    id: int
    student_id: int
    document_type: str
    filename: str
    status: str

    model_config = ConfigDict(from_attributes=True)

class RegisterRequest(StudentCreate):
    email: str = Field(min_length=5, max_length=255, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    student: "AuthenticatedStudentResponse"


class AuthenticatedStudentResponse(StudentResponse):
    email: str
