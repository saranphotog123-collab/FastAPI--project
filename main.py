from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

students = []

@app.get("/health")
def health_check():
    return {"status": "healthy"}


class Student(BaseModel):
    name: str
    age: int
    department: str
    email: str


@app.post("/students")
def create_student(student: Student):
    students.append(student)
    return student


@app.get("/students")
def list_students():
    return students


@app.put("/students")
def update_student(student: Student):
    return student