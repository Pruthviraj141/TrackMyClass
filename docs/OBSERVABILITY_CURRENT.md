# Current Observability Audit

Before Phase 8, TrackMyClass possessed:
- **Print statements** scattered across ML ingestion frames.
- **Python logging:** Basic `logging.getLogger(__name__)` used in FastAPI WS scopes (`monitor_ws.py`).
- **Correlation IDs:** Phase 2 introduced basic UUID generation exclusively mapped into FastApi request lifecycles structurally, but it failed to append into the inference components uniquely.
- **Sensitive logs:** Raw exception strings occasionally drop Base64 bindings or tensor output formats locally which consumes extreme console IO throughput.

**Goals for Resolution:**
- Standardize Python's `logging` to use JSON format outputs globally.
- Redact Base64 completely avoiding stdout stringification.
- Pipe `correlation_id` natively into `WorkerManager.submit_frame()` passing to `Multiprocessing.Queue`.
