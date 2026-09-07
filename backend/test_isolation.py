import os
import sys

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.infrastructure.database.sqlite_impl import (
    _get_connection,
    add_student,
    get_all_students,
    delete_student,
    add_attendance,
    get_attendance_by_date
)

def setup_test_db():
    print("Setting up test database...")
    # Clear existing data for tests if needed, or we can just use unique IDs
    pass

def test_tenant_isolation():
    print("Running Tenant Isolation Tests...")
    
    tenant_A = "COLLEGE_A"
    tenant_B = "COLLEGE_B"
    
    # 1. Add students to different tenants
    print(f"Adding students to {tenant_A} and {tenant_B}...")
    add_student(tenant_A, "student_A1", "Alice", "A01", "Female", [0.1]*128)
    add_student(tenant_B, "student_B1", "Bob", "B01", "Male", [0.2]*128)
    
    # 2. Verify isolation on get_all_students
    students_A = get_all_students(tenant_A)
    students_B = get_all_students(tenant_B)
    
    assert any(s["student_id"] == "student_A1" for s in students_A), "Tenant A should see student_A1"
    assert not any(s["student_id"] == "student_B1" for s in students_A), "Tenant A should NOT see student_B1"
    
    assert any(s["student_id"] == "student_B1" for s in students_B), "Tenant B should see student_B1"
    assert not any(s["student_id"] == "student_A1" for s in students_B), "Tenant B should NOT see student_A1"
    print("✅ get_all_students respects tenant isolation")
    
    # 3. Add attendance
    print("Adding attendance records...")
    add_attendance(tenant_A, "student_A1", "Alice", "session_A", "Math", "2026-01-01", "09:00", "2026-01-01T09:00:00", 0.95)
    add_attendance(tenant_B, "student_B1", "Bob", "session_B", "Science", "2026-01-01", "10:00", "2026-01-01T10:00:00", 0.95)
    
    # 4. Verify isolation on attendance
    att_A = get_attendance_by_date(tenant_A, "2026-01-01")
    att_B = get_attendance_by_date(tenant_B, "2026-01-01")
    
    assert any(a["student_id"] == "student_A1" for a in att_A), "Tenant A should see Alice's attendance"
    assert not any(a["student_id"] == "student_B1" for a in att_A), "Tenant A should NOT see Bob's attendance"
    
    assert any(a["student_id"] == "student_B1" for a in att_B), "Tenant B should see Bob's attendance"
    assert not any(a["student_id"] == "student_A1" for a in att_B), "Tenant B should NOT see Alice's attendance"
    print("✅ get_attendance_by_date respects tenant isolation")
    
    # 5. Verify deletion isolation
    print("Testing delete_student isolation...")
    success_b_deletes_a = delete_student(tenant_B, "student_A1")
    assert not success_b_deletes_a, "Tenant B should NOT be able to delete Tenant A's student"
    
    success_a_deletes_a = delete_student(tenant_A, "student_A1")
    assert success_a_deletes_a, "Tenant A should be able to delete its own student"
    
    # Verify cascading delete
    att_A_after = get_attendance_by_date(tenant_A, "2026-01-01")
    assert not any(a["student_id"] == "student_A1" for a in att_A_after), "Attendance should be deleted with student"
    
    # Clean up Bob
    delete_student(tenant_B, "student_B1")
    print("✅ delete_student respects tenant isolation and cascading rules")
    
    print("\nAll Tenant Isolation Tests Passed! 🎉")

if __name__ == "__main__":
    setup_test_db()
    test_tenant_isolation()
