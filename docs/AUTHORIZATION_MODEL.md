# Authorization Model

To assure Phase 2 compliance, the RBAC Matrix defines explicitly which roles contain authority to execute Use Case operations over specific bounded endpoints.

## Matrix

| Operation                          | SUPER_ADMIN | INSTITUTION_ADMIN | TEACHER | STUDENT |
|------------------------------------|-------------|-------------------|---------|---------|
| Create Institution                 | YES         | NO                | NO      | NO      |
| Add Teachers                       | YES         | YES               | NO      | NO      |
| Register Students (enroll images)  | YES         | YES               | YES     | NO      |
| Delete Students                    | YES         | YES               | NO      | NO      |
| Start Attendance Session           | YES         | YES               | YES     | NO      |
| Mark Real-time Frames              | YES         | YES               | YES     | NO      |
| View Any Class Attendance          | YES         | YES               | YES     | NO      |
| View Own Attendance                | YES         | YES               | YES     | YES     |

## Validation Execution
When a TEACHER tries to hit `/api/v1/attendance/session/start`, the FastAPI router utilizes `Depends(require_role(institution_id, [Role.TEACHER, Role.INSTITUTION_ADMIN]))`. 

The `get_current_user_from_token` function rips the JWT out of `.cookies` (or `Authorization: Bearer`), validates the Cryptographic Signature using PyJWT, then executes a Tenant verification that the specific user has an explicit cross-over joining their identifier to the `institution_id` requested.

If the teacher inputs an `institution_id` they do not belong to, `Insufficient Privileges (403)` is raised blocking all execution entirely.
