from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()

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
    return student
