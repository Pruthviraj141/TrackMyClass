# Multi-Tenancy Architecture

## Goal
Institution A must never access Institution B's data under any circumstance.

## Root Strategy
We enforce tenant isolation structurally at the Application layer and Database layer. Clients can *never* override their assigned `institution_id` parameter directly through unauthenticated fields. 

## Trust Model (Step 3 Constraints)
Never accept raw inputs as proof of context:
* `institution_id`
* `student_id`
* `session_id`

### Entity Binding
1. **User**: Global entry (can belong to multiple organizations like an Instructor teaching across two campuses).
2. **Student**: 100% bound to an `institution_id`.
3. **Session**: 100% bound to an `institution_id`.
4. **AttendanceRecord**: Derives bounding strictly from the bound `Session` and `Student` intersecting it.

## Execution Rules
Every API request MUST extract the `institution_id` natively from the Decoded JWT `InstitutionMembership` dependencies rather than relying on HTTP payload parameters logically overriding the context.

If `api/v1/attendance` triggers, the Context Object injected by `FastAPI Depends()` strictly injects the token's authenticated Tenant array. Extraneous institutions automatically throw `401 Unauthorized` or `403 Forbidden`.
