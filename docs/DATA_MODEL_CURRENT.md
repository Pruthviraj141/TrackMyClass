# Current Data Model (Step 5)

Analyzed primarily via `backend/database/sqlite_service.py`. Dual implementation strategy exists between SQLite (local development fallback) and Firebase Firestore (cloud integration). Structure mapping shown pertains to SQL schema abstraction.

## Entities Overview

### 1. `institutions` (Multi-tenant structure scaffolding)
- **`code`** (TEXT, Primary Key): ID handle, typically "DEMO2026" as defaulted across queries.
- **`name`** (TEXT): Institution Display Name.
- **`active`** (INTEGER): Boolean 1/0 status.

### 2. `students`
Holds core biometric definitions and demographic profiles.
- **`student_id`** (TEXT, Primary Key): Unique UUIDv4 UUID.
- **`institution_id`** (TEXT): Tenant reference ("DEMO2026").
- **`name`** (TEXT): Student display name.
- **`roll_number`** (TEXT): Registration index.
- **`gender`** (TEXT): Demographics identifier ('male', 'female', 'other').
- **`embedding`** (TEXT): JSON Serialized Payload array of 512 dimensions (Float32 values representing FaceNet features).
- **`password`** (TEXT): Hashed string entry placeholder for future self-login portals.
- **`created_at`** (TEXT): ISO format timestamp string.

### 3. `attendance`
Event log appending transactional proofs of recognition.
- **`id`** (INTEGER, Primary Key / Increment): Internal ID.
- **`institution_id`** (TEXT): Tenant reference.
- **`student_id`** (TEXT): Foreign key linking back to `students` table.
- **`name`** (TEXT): Denormalized text field containing student name at exact scan time.
- **`session_id`** (TEXT): GUID tying record to a specific teacher tracking span.
- **`subject_name`** (TEXT): The target subject.
- **`date`** (TEXT): Formatted 'YYYY-MM-DD'.
- **`time`** (TEXT): Exact HH:MM:SS event.
- **`timestamp`** (TEXT): ISO formatting containing exact millisecond representation.
- **`confidence`** (REAL): The recognized confidence decimal.

## Analysis Notes & Weaknesses
* Both Databases are fully active fallback setups. SQLite is robust but holds lists (`embedding`) poorly formatted inside stringified Text JSON. Firebase maps native lists cleanly.
* Identical interfaces, effectively hiding NO-SQL versus SQL characteristics from the app core mapping identical structures.
* Needs stricter cross-relations (Only implicit linkage applied within SQLite schema definition outside of `FOREIGN KEY (student_id) REFERENCES students(student_id)`).
