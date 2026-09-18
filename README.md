# Student Management API

## Overview

Student Management API is a FastAPI backend application for managing student records.

### Features

* User authentication
* JWT token-based login
* Student creation
* Student listing
* Student search
* Department filtering
* Student update
* User-based authorization
* PostgreSQL database
* Alembic migrations
* Automated testing
* Swagger API documentation

## Technology Stack

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* JWT
* Pytest

---

## 1. Project Setup

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy alembic python-dotenv python-jose passlib httpx pytest python-multipart pg8000
```

---

## 2. Environment Configuration

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=postgresql+pg8000://<username>:<password>@localhost:5432/student_db
```

Replace the username and password with your PostgreSQL credentials.

The `.env` file should not be committed to Git.

---

## 3. Database Migration

This project uses Alembic for database migrations.

### Create Migration

```bash
alembic revision --autogenerate -m "migration message"
```

Example:

```bash
alembic revision --autogenerate -m "create students table"
```

### Apply Migration

```bash
alembic upgrade head
```

### Check Current Migration

```bash
alembic current
```

### View Migration History

```bash
alembic history
```

---

## 4. Run the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The application runs at:

```text
http://127.0.0.1:8000
```

---

## 5. API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

OpenAPI JSON:

```text
http://127.0.0.1:8000/openapi.json
```

---

## 6. API Endpoints

### GET /health

Checks whether the API is running.

Response:

```json
{
    "status": "healthy"
}
```

---

### POST /login

Authenticates a user and returns an access token.

The login request uses form data:

```text
username=admin@example.com
password=admin123
```

Successful response:

```json
{
    "access_token": "<JWT token>",
    "token_type": "bearer"
}
```

The access token is required for protected endpoints.

---

### POST /students

Creates a new student.

Authentication is required.

Request body:

```json
{
    "name": "John",
    "age": 20,
    "department": "AI & DS",
    "email": "john@example.com"
}
```

The created student is associated with the authenticated user.

---

### GET /students

Returns students belonging to the authenticated user.

Authentication is required.

#### Search by name

```text
/students?search=John
```

#### Filter by department

```text
/students?department=AI%20%26%20DS
```

#### Search and filter together

```text
/students?search=John&department=AI%20%26%20DS
```

---

### PUT /students/{student_id}

Updates an existing student.

Authentication is required.

Request body:

```json
{
    "name": "Updated Student",
    "age": 21,
    "department": "AI & DS",
    "email": "updated@example.com"
}
```

A user can update only their own student records.

If the student belongs to another user, the API returns:

```json
{
    "detail": "Access denied"
}
```

with status code `403`.

---

## 7. Authentication and Authorization

The API uses JWT authentication.

Authentication flow:

```text
User
  ↓
POST /login
  ↓
Validate credentials
  ↓
Generate JWT token
  ↓
Bearer Token
  ↓
Access protected endpoints
```

Authorization ensures that users can access and modify only their own student records.

---

## 8. Error Handling

### 401 Unauthorized

Returned when authentication fails or a valid token is not provided.

### 403 Forbidden

Returned when a user tries to access or modify another user's student record.

### 404 Not Found

Returned when the requested user or student does not exist.

### 422 Unprocessable Entity

Returned when the request data fails validation.

### 500 Internal Server Error

Returned when an unexpected database or service error occurs.

---

## 9. Automated Testing

Tests are located in:

```text
tests/test_main.py
```

Run the tests using:

```bash
python -m pytest -v
```

The tests cover:

* Health check
* Login
* Student creation
* Validation
* Authentication
* Authorization
* Service failure

---

## 10. Project Structure

```text
Day 1/
│
├── alembic/
│   └── versions/
│
├── services/
│   ├── __init__.py
│   └── student_service.py
│
├── tests/
│   ├── .gitignore
│   └── test_main.py
│
├── .env
├── .gitignore
├── alembic.ini
├── api-design.md
├── auth.py
├── database.py
├── main.py
├── models.py
└── README.md
```

---

## 11. Complete Run Process

Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Apply database migrations:

```bash
alembic upgrade head
```

Start the application:

```bash
uvicorn main:app --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

Run automated tests:

```bash
python -m pytest -v
```

---

## 12. OpenAPI Metadata

The FastAPI application provides the following OpenAPI metadata:

**Title:** Student Management API

**Version:** 1.0.0

**Description:** A FastAPI backend for student management with authentication, authorization, search, filtering, and database integration.
## Deployment Checklist

- Production environment variables configured
- `.env` excluded from Git
- Database migrations completed
- Production startup command verified
- Health check verified
- Authentication and authorization verified
- Student CRUD operations tested
- Search and filtering tested
- Automated tests passed
- Application logs checked