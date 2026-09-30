import hashlib
import hmac
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .schemas import (
    AuthResponse,
    AuthenticatedStudentResponse,
    LoginRequest,
    RegisterRequest,
    StudentResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), 200_000
    ).hex()


def _issue_token(user: models.User, db: Session) -> str:
    token = secrets.token_hex(32)
    db.add(models.AuthToken(token=token, user_id=user.id))
    db.commit()
    return token


def _student_response(student: models.Student, email: str) -> AuthenticatedStudentResponse:
    return AuthenticatedStudentResponse(
        **StudentResponse.model_validate(student).model_dump(),
        email=email,
    )


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=409, detail="This email is already registered")

    student = models.Student(
        **data.model_dump(exclude={"email", "password"})
    )
    db.add(student)
    db.flush()

    salt = secrets.token_hex(16)
    user = models.User(
        student_id=student.id,
        email=email,
        password_salt=salt,
        password_hash=_hash_password(data.password, salt),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(student)
    return AuthResponse(token=_issue_token(user, db), student=_student_response(student, email))


@router.post("/login", response_model=AuthResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email.strip().lower()).first()
    expected = _hash_password(data.password, user.password_salt) if user else ""
    if user is None or not hmac.compare_digest(expected, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    student = db.get(models.Student, user.student_id)
    return AuthResponse(
        token=_issue_token(user, db),
        student=_student_response(student, user.email),
    )


@router.get("/me", response_model=StudentResponse)
def me(authorization: str = Header(default=""), db: Session = Depends(get_db)):
    token = authorization.removeprefix("Bearer ").strip()
    record = db.get(models.AuthToken, token) if token else None
    user = db.get(models.User, record.user_id) if record else None
    student = db.get(models.Student, user.student_id) if user else None
    if student is None:
        raise HTTPException(status_code=401, detail="Not signed in")
    return _student_response(student, user.email)
