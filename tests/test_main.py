from fastapi.testclient import TestClient

from main import app
from auth import hash_password
from database import SessionLocal
from models import User


client = TestClient(app)


def get_token():
    response = client.post(
        "/login",
        data={
            "username": "admin@example.com",
            "password": "admin123"
        }
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def get_token_for_user(username, password):
    response = client.post(
        "/login",
        data={
            "username": username,
            "password": password
        }
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_login():
    response = client.post(
        "/login",
        data={
            "username": "admin@example.com",
            "password": "admin123"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_create_student():
    token = get_token()

    response = client.post(
        "/students",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Test Student",
            "age": 20,
            "department": "AI & DS",
            "email": "teststudent@example.com"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test Student"
    assert data["age"] == 20
    assert data["department"] == "AI & DS"


def test_create_student_validation_failure():
    token = get_token()

    response = client.post(
        "/students",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Invalid Student",
            "age": "not-a-number",
            "department": "AI & DS",
            "email": "invalid@example.com"
        }
    )

    assert response.status_code == 422


def test_students_requires_authentication():
    response = client.get("/students")

    assert response.status_code == 401


def test_create_student_service_failure(monkeypatch):
    token = get_token()

    def fake_create_student(*args, **kwargs):
        raise Exception("Simulated service failure")

    monkeypatch.setattr(
        "main.create_student_service",
        fake_create_student
    )

    response = client.post(
        "/students",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "name": "Failure Test",
            "age": 20,
            "department": "AI & DS",
            "email": "failure@example.com"
        }
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to create student"


def test_user_cannot_update_another_users_student():
    db = SessionLocal()

    try:
        user2 = db.query(User).filter(
            User.email == "user2@example.com"
        ).first()

        if not user2:
            user2 = User(
                name="User Two",
                email="user2@example.com",
                password_hash=hash_password("user2123")
            )
            db.add(user2)
            db.commit()
        else:
            user2.password_hash = hash_password("user2123")
            db.commit()

    finally:
        db.close()

    token1 = get_token()

    token2 = get_token_for_user(
        "user2@example.com",
        "user2123"
    )

    create_response = client.post(
        "/students",
        headers={
            "Authorization": f"Bearer {token1}"
        },
        json={
            "name": "Owner Student",
            "age": 21,
            "department": "AI & DS",
            "email": "ownerstudent@example.com"
        }
    )

    assert create_response.status_code == 200

    student_id = create_response.json()["id"]

    response = client.put(
        f"/students/{student_id}",
        headers={
            "Authorization": f"Bearer {token2}"
        },
        json={
            "name": "Unauthorized Update",
            "age": 22,
            "department": "AI & DS",
            "email": "unauthorized@example.com"
        }
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"