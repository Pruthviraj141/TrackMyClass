from typing import List
from backend.domain.entities import AttendanceRecord
from backend.core.config import DATABASE_MODE

if DATABASE_MODE == "firebase":
    from backend.infrastructure.database.firebase_impl import (
        add_attendance,
        get_attendance_by_date,
        delete_attendance_by_date
    )
else:
    from backend.infrastructure.database.sqlite_impl import (
        add_attendance,
        get_attendance_by_date,
        delete_attendance_by_date
    )

class AttendanceRepository:
    def add(self, record: AttendanceRecord) -> bool:
        return add_attendance(
            institution_id=record.institution_id,
            student_id=record.student_id,
            name=record.name,
            session_id=record.session_id,
            subject_name=record.subject_name,
            date=record.date,
            time=record.time,
            timestamp=record.timestamp,
            confidence=record.confidence
        )

    def get_by_date(self, institution_id: str, date: str) -> List[AttendanceRecord]:
        raw_records = get_attendance_by_date(institution_id, date)
        records = []
        for r in raw_records:
            records.append(AttendanceRecord(
                id=r.get("id"),
                institution_id=institution_id,
                student_id=r.get("student_id"),
                name=r.get("name"),
                session_id=r.get("session_id"),
                subject_name=r.get("subject_name", ""),
                date=r.get("date", date),
                time=r.get("time", ""),
                timestamp=r.get("timestamp"),
                confidence=r.get("confidence", 0.0)
            ))
        return records

    def delete_by_date(self, institution_id: str, student_id: str, date: str, session_id: str = None) -> bool:
        return delete_attendance_by_date(institution_id, student_id, date, session_id)
