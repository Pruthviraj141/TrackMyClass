# TrackMyClass Threat Model (Phase 2)

## 1. STRIDE Analysis
- **Spoofing**: Handled via proper JWT decoding and robust PyJWT HMAC checks preventing token forgery.
- **Tampering**: Blocked by JWT signature schemas; Database inputs scrubbed via Pydantic.
- **Repudiation**: Centralized Audit Logging traces `LOGIN_ATTEMPT` metrics tied to Request IDs tracking lifecycle endpoints.
- **Information Disclosure**: Mitigated via explicit `embedding=[]` scrubs enforcing biometric cloaking.
- **Denial of Service**: Mitigated via In-Memory rate limiting boundaries (`MAX_REQUESTS / WINDOW`), alongside 3MB Payload chunking (`MAX_BASE64_LENGTH`).
- **Elevation of Privilege**: Stopped natively via structured Tenant Cross-Routing constraints injecting exactly matched Identity Roles explicitly checking `institution_id` dependencies.

## 2. Unmitigated Risks (Phase 3+)
* Rate Limiters are currently non-distributed and lose state on restarts (Moved to Redis roadmap).
* PyTorch ML Blocks the ASGI event loop thread making application easily susceptible to CPU-exhaustion (Moved to Async Workers roadmap).
