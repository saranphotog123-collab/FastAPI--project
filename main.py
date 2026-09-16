from datetime import datetime, timedelta
from typing import Optional
import logging

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from auth import verify_password
from database import SessionLocal
from models import User, Student as StudentDB
from services.student_service import create_student as create_student_service


# --------------------------------------------------
# App and Logging
# --------------------------------------------------

app = FastAPI(
    title="Student Management API",
    description="A FastAPI backend for student management with authentication, authorization, search, filtering, and database integration.",
    version="1.0.0"
)



logger = logging.getLogger(__name__)


# --------------------------------------------------
# Database session
# --------------------------------------------------

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# --------------------------------------------------
# JWT settings
# --------------------------------------------------

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# --------------------------------------------------
# Request model
# --------------------------------------------------

class StudentCreate(BaseModel):
    name: str
    age: int
    department: str
    email: str


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.get("/health")
def health_check():
    logger.info("Health check requested")

    return {"status": "healthy"}


# --------------------------------------------------
# Create JWT token
# --------------------------------------------------

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# --------------------------------------------------
# Verify JWT token
# --------------------------------------------------

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return username

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


# --------------------------------------------------
# Login
# --------------------------------------------------

@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.password_hash
    ):
        logger.warning(
            "Failed login attempt for %s",
            form_data.username
        )

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        {"sub": user.email}
    )

    logger.info(
        "User logged in successfully: %s",
        user.email
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# --------------------------------------------------
# Create student
# --------------------------------------------------

@app.post("/students")
def create_student(
    student: StudentCreate,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == username
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    try:
        new_student = create_student_service(
            db=db,
            student_data=student,
            owner_id=user.id
        )

        logger.info(
            "Student created: student_id=%s owner_id=%s",
            new_student.id,
            user.id
        )

        return {
            "id": new_student.id,
            "name": new_student.name,
            "age": new_student.age,
            "department": new_student.department,
            "email": new_student.email,
            "owner_id": new_student.owner_id
        }

    except Exception:
        db.rollback()

        logger.exception(
            "Failed to create student for owner_id=%s",
            user.id
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to create student"
        )


# --------------------------------------------------
# Search and filters
# --------------------------------------------------

@app.get("/students")
def list_students(
    search: Optional[str] = Query(default=None),
    department: Optional[str] = Query(default=None),
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == username
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    query = db.query(StudentDB).filter(
        StudentDB.owner_id == user.id
    )

    if search:
        query = query.filter(
            StudentDB.name.ilike(f"%{search}%")
        )

    if department:
        query = query.filter(
            StudentDB.department == department
        )

    students = query.all()

    logger.info(
        "Student search performed by owner_id=%s",
        user.id
    )

    return [
        {
            "id": student.id,
            "name": student.name,
            "age": student.age,
            "department": student.department,
            "email": student.email,
            "owner_id": student.owner_id
        }
        for student in students
    ]


# --------------------------------------------------
# Update student
# --------------------------------------------------

@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    updated_student: StudentCreate,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == username
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    student = db.query(StudentDB).filter(
        StudentDB.id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    # Authorization check
    if student.owner_id != user.id:
        logger.warning(
            "Unauthorized update attempt: student_id=%s owner_id=%s",
            student_id,
            user.id
        )

        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    student.name = updated_student.name
    student.age = updated_student.age
    student.department = updated_student.department
    student.email = updated_student.email

    try:
        db.commit()
        db.refresh(student)

        logger.info(
            "Student updated: student_id=%s owner_id=%s",
            student.id,
            user.id
        )

    except Exception:
        db.rollback()

        logger.exception(
            "Failed to update student: student_id=%s",
            student_id
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to update student"
        )

    return {
        "id": student.id,
        "name": student.name,
        "age": student.age,
        "department": student.department,
        "email": student.email,
        "owner_id": student.owner_id
    }