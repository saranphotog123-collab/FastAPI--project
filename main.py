from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import jwt, JWTError

from auth import hash_password, verify_password


app = FastAPI()

students = []

# JWT settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Student model
class Student(BaseModel):
    name: str
    age: int
    department: str
    email: str


# Create JWT token
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


# Verify JWT token
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


# Login
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    username = form_data.username
    password = form_data.password

    # Temporary test user
    if username != "admin" or password != "admin123":
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        {"sub": username}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# Create student
@app.post("/students")
def create_student(student: Student):
    students.append(student)
    return student


# Protected students endpoint
@app.get("/students")
def list_students(
    username: str = Depends(verify_token)
):
    return students


# Update student
@app.put("/students")
def update_student(student: Student):
    return student