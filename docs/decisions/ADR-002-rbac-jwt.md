# ADR 002: JWT and RBAC Implementation

## Status
Accepted

## Context
Phase 1 extracted a layered architecture cleanly, but Phase 0 possessed a critical vulnerability using hardcoded single-admin plaintext authentication against SQLite boundaries risking system takeover easily. We need a modern Identity enforcement pattern securing Tenant bounds.

## Decision
We chose stateless JWT Tokens via PyJWT alongside standard bcrypt hashing mechanisms mapped via FastAPI generic dependencies (`Depends()`).

## Consequences
Stateless JWT constraints significantly lower SQLite IO contention compared to standard `auth_sessions_table` polling, but sacrifices immediate global revocation without utilizing a Redis blacklisting cluster (Deferred to Phase 3). We explicitly decouple Domain logic via Pydantic mapping isolating HTTP bounds securely.
