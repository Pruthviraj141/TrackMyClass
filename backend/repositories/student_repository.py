from typing import List, Optional
from backend.domain.entities import Student
from backend.core.config import DATABASE_MODE

if DATABASE_MODE == "firebase":
    from backend.infrastructure.database.firebase_impl import (
        add_student,
        get_all_students,
        delete_student,
        update_student_embedding
    )
else:
    from backend.infrastructure.database.sqlite_impl import (
        add_student,
        get_all_students,
        delete_student,
        update_student_embedding
    )

class StudentRepository:
    def add(self, student: Student) -> bool:
        return add_student(
            institution_id=student.institution_id,
            student_id=student.student_id,
            name=student.name,
            roll_number=student.roll_number,
            gender=student.gender,
            embedding=student.embedding,
            password=student.password or ""
        )

    def get_all(self, institution_id: str) -> List[Student]:
        raw_students = get_all_students(institution_id)
        students = []
        for s in raw_students:
            students.append(Student(
                student_id=s.get("student_id"),
                institution_id=s.get("institution_id", institution_id),
                name=s.get("name"),
                roll_number=s.get("roll_number"),
                gender=s.get("gender"),
                embedding=s.get("embedding", []),
                created_at=s.get("created_at")
            ))
        return students

    def delete(self, institution_id: str, student_id: str) -> bool:
        return delete_student(institution_id, student_id)

    def update_embedding(self, institution_id: str, student_id: str, embedding: list) -> bool:
        return update_student_embedding(institution_id, student_id, embedding)
