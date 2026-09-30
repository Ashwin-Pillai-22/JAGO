from pathlib import Path
from mimetypes import guess_type
from typing import Annotated, Literal
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from fastapi import File, Form, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .database import get_db, initialize_database
from . import models
from .auth import router as auth_router
from .chatbot import create_chat_response
from .schemas import (
    ChatRequest,
    ChatResponse,
    ScholarshipResponse,
    ScholarshipStatisticsResponse,
    StudentCreate,
    StudentDocumentResponse,
    StudentResponse,
)


app = FastAPI(
    title="JAGO Scholarship API",
    description="Unified ST Scholarship Prototype",
    version="1.0.0"
)


app.include_router(auth_router)

initialize_database()

UPLOAD_DIRECTORY = Path(__file__).resolve().parent.parent / "uploads"
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024
ALLOWED_DOCUMENT_TYPES = {".pdf", ".png", ".jpg", ".jpeg"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/students", response_model=StudentResponse, status_code=201)
def create_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    student = models.Student(**student_data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@app.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(models.Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.get("/students", response_model=list[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    student = db.get(models.Student, request.student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return create_chat_response(student, request.message, db)


@app.post(
    "/students/{student_id}/documents",
    response_model=StudentDocumentResponse,
    status_code=201,
)
async def upload_student_document(
    student_id: int,
    document_type: Annotated[
        Literal[
            "aadhaar",
            "domicile",
            "caste",
            "marksheet_10",
            "marksheet_12",
            "graduation",
            "post_graduation",
        ],
        Form(),
    ],
    file: Annotated[UploadFile, File()],
    db: Session = Depends(get_db),
):
    student = db.get(models.Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Upload a PDF, PNG, or JPEG document",
        )

    content = await file.read(MAX_DOCUMENT_SIZE + 1)
    if len(content) > MAX_DOCUMENT_SIZE:
        raise HTTPException(status_code=413, detail="Document must be 10 MB or smaller")

    valid_signature = (
        (suffix == ".pdf" and content.startswith(b"%PDF-"))
        or (suffix == ".png" and content.startswith(b"\x89PNG\r\n\x1a\n"))
        or (suffix in {".jpg", ".jpeg"} and content.startswith(b"\xff\xd8\xff"))
    )
    if not valid_signature:
        raise HTTPException(status_code=400, detail="File content does not match its extension")

    stored_name = f"{uuid4().hex}{suffix}"
    student_directory = UPLOAD_DIRECTORY / str(student_id)
    student_directory.mkdir(parents=True, exist_ok=True)
    storage_path = student_directory / stored_name
    storage_path.write_bytes(content)

    document = models.StudentDocument(
        student_id=student_id,
        document_type=document_type,
        filename=Path(file.filename or stored_name).name,
        storage_path=str(storage_path),
        status="submitted",
    )
    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        storage_path.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

    return document


@app.get("/students/{student_id}/documents", response_model=list[StudentDocumentResponse])
def get_student_documents(
    student_id: int,
    db: Session = Depends(get_db),
):
    student = db.get(models.Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return (
        db.query(models.StudentDocument)
        .filter(models.StudentDocument.student_id == student_id)
        .order_by(models.StudentDocument.id.desc())
        .all()
    )


@app.get("/students/{student_id}/documents/{document_id}")
def show_student_document(
    student_id: int,
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(models.StudentDocument)
        .filter(
            models.StudentDocument.id == document_id,
            models.StudentDocument.student_id == student_id,
        )
        .first()
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = Path(document.storage_path)
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Stored document is unavailable")
    return FileResponse(
        file_path,
        filename=document.filename,
        media_type=guess_type(document.filename)[0] or "application/octet-stream",
        content_disposition_type="inline",
    )


@app.get("/scholarships", response_model=list[ScholarshipResponse])
def get_scholarships(
    category: str | None = None,
    education_level: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Scholarship)
    if category:
        query = query.filter(models.Scholarship.category == category)
    if education_level:
        query = query.filter(models.Scholarship.education_level == education_level)
    return query.all()


def _get_scholarships_by_scheme(
    scheme: str,
    db: Session,
):
    return db.query(models.Scholarship).filter(models.Scholarship.scheme == scheme).all()


@app.get("/scholarships/pre-matric", response_model=list[ScholarshipResponse])
def get_pre_matric_scholarships(
    db: Session = Depends(get_db),
):
    return _get_scholarships_by_scheme("Pre-Matric Scholarship", db)


@app.get("/scholarships/post-matric", response_model=list[ScholarshipResponse])
def get_post_matric_scholarships(
    db: Session = Depends(get_db),
):
    return _get_scholarships_by_scheme("Post-Matric Scholarship", db)


@app.get("/scholarships/top-class", response_model=list[ScholarshipResponse])
def get_top_class_scholarships(
    db: Session = Depends(get_db),
):
    return _get_scholarships_by_scheme("Top Class Scholarship", db)


@app.get("/scholarships/national", response_model=list[ScholarshipResponse])
def get_national_scholarships(
    db: Session = Depends(get_db),
):
    return _get_scholarships_by_scheme("National Scholarship", db)


@app.get("/scholarships/national-fellowship", response_model=list[ScholarshipResponse])
def get_national_fellowship_scholarships(
    db: Session = Depends(get_db),
):
    return _get_scholarships_by_scheme("National Fellowship (NFST)", db)


@app.get("/scholarships/national-overseas", response_model=list[ScholarshipResponse])
def get_national_overseas_scholarships(
    db: Session = Depends(get_db),
):
    return _get_scholarships_by_scheme("National Overseas Scholarship (NOS)", db)


@app.get("/scholarships/{scholarship_id}", response_model=ScholarshipResponse)
def get_scholarship(scholarship_id: int, db: Session = Depends(get_db)):
    scholarship = db.get(models.Scholarship, scholarship_id)
    if scholarship is None:
        raise HTTPException(status_code=404, detail="Scholarship not found")
    return scholarship


@app.get("/statistics", response_model=list[ScholarshipStatisticsResponse])
def get_statistics(
    scheme: str | None = None,
    financial_year: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.ScholarshipStatistics)
    if scheme:
        query = query.filter(models.ScholarshipStatistics.scheme == scheme)
    if financial_year:
        query = query.filter(models.ScholarshipStatistics.financial_year == financial_year)
    return query.all()