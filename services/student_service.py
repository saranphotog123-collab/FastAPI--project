import logging

from sqlalchemy.orm import Session
from models import Student


logger = logging.getLogger(__name__)


def create_student(db: Session, student_data, owner_id: int):
    try:
        new_student = Student(
            name=student_data.name,
            age=student_data.age,
            department=student_data.department,
            email=student_data.email,
            owner_id=owner_id
        )

        db.add(new_student)
        db.commit()
        db.refresh(new_student)

        logger.info(
            "Student created successfully: student_id=%s owner_id=%s",
            new_student.id,
            owner_id
        )

        return new_student

    except Exception:
        db.rollback()

        logger.exception(
            "Failed to create student: owner_id=%s",
            owner_id
        )

        raise