# Recovery Runbook

*Executable recovery procedures for TrackMyClass Backend Infrastructure.*

## 1. What happens if the API fails?
- **Symptom:** Clients get 502 Bad Gateway or Timeout. Front-end Websocket disconnects.
- **Action:** Restart FastApi or scaled Uvicorn workers. Docker/Systemd typically handles this inherently. 
- **Verification:** Monitor `GET /api/v1/auth/health` returns 200.

## 2. What happens if the ML Worker fails?
- **Symptom:** System remains completely online, but faces are detected with NO matching output over Websockets (status stays empty).
- **Action:** Standard implementation has `worker_manager` automatically restarting failed multiprocessing hooks. If it hangs permanently, restart the API container manually triggering total cascade restart.
- **Verification:** Observe UI mapping "Processing... frames" resuming valid matches inherently.

## 3. What happens if Redis fails?
- **Symptom:** Token-bucket warns in console. Realtime caches missing. 
- **Action:** Restart `redis-trackmyclass`. The python client explicitly reconnects without manual intervention naturally restoring sliding limits.
- **Verification:** Check `docker logs trackmyclass-backend`. It will explicitly declare "Redis Connection Restored."

## 4. What happens if the DB fails?
- **Symptom:** HTTP 500s on all hard creation elements. Web sockets drop completely when attempting to mark attendance.
- **Action:** Recover SQLite `.db` or restore Firebase connection strings depending on configuration mode.

*Test all recovery elements iteratively after major infrastructure patches!*
