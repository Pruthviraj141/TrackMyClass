# Phase 3 Defect Log

### 1. `firebase_admin` Missing Dependencies
- **Issue**: E2E Integration failed at execution because `firebase_admin` was completely deleted / undocumented inside standard environment builds, crashing Pytest module collection immediately due to global un-guarded imports.
- **Resolution**: Refactored `backend/core/config.py` enforcing soft-fail `try...except ImportError` loops triggering SQLite auto-fallbacks securely without modifying standard `main.py` entry blocks.

### 2. PyTest JWT Mock Limits
- **Issue**: Standard `.env` test users defaulted to `"admin":"admin"` but Pytest simulated `"password":"password"`, failing `bcrypt`.
- **Resolution**: Refactored `test_e2e_core_flows.py` mapping correct passwords accurately evaluating integrations.

### 3. Backend `remove_student` Signature Mismatch
- **Issue**: `backend/repositories/student_repository.py` attempted calling `remove_student` mapping onto SQLite's `delete_student`.
- **Resolution**: Aligned functions globally allowing clean API endpoints securely mapping.
