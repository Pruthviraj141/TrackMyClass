import asyncio
import time
import os
import httpx
import websockets

def _make_dummy_frame(size_kb: int = 30) -> bytes:
    return b"\xff\xd8\xff" + os.urandom(size_kb * 1024)

async def hammer_dashboard(token: str, duration_s: float):
    latencies = []
    end_time = time.monotonic() + duration_s
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        while time.monotonic() < end_time:
            t0 = time.monotonic()
            try:
                resp = await client.get("/api/v1/admin/dashboard-data", headers={"Authorization": f"Bearer {token}"})
                dt = time.monotonic() - t0
                if resp.status_code == 200: latencies.append(dt)
            except Exception: pass
            await asyncio.sleep(0.01)
    return latencies

async def run_ws_session(session_id: str, token: str, duration_s: float):
    end_time = time.monotonic() + duration_s
    url = f"ws://localhost:8000/api/v1/ws/monitor/{session_id}?token={token}"
    frames_sent, results_received = 0, 0
    try:
        async with websockets.connect(url) as ws:
            await ws.recv()
            while time.monotonic() < end_time:
                await ws.send(_make_dummy_frame())
                frames_sent += 1
                try:
                    await asyncio.wait_for(ws.recv(), timeout=0.5)
                    results_received += 1
                except asyncio.TimeoutError: pass
                await asyncio.sleep(0.2)
    except Exception as e: print(f"WS error: {e}")
    return frames_sent, results_received

async def main():
    async with httpx.AsyncClient() as client:
        resp = await client.post("http://localhost:8000/api/v1/auth/token", data={"username": "admin", "password": "adminpassword"})
        token = resp.json().get("access_token")
        
        await client.post("http://localhost:8000/api/v1/attendance/session/end", headers={"Authorization": f"Bearer {token}"})
        resp = await client.post("http://localhost:8000/api/v1/attendance/session/start", json={"subject_name": "Bench"}, headers={"Authorization": f"Bearer {token}"})
        session_id = resp.json()["session_id"]

    dur = 5.0
    ws_task = asyncio.create_task(run_ws_session(session_id, token, dur))
    http_task = asyncio.create_task(hammer_dashboard(token, dur))
    frames, results = await ws_task
    latencies = await http_task
    
    avg_ping = sum(latencies) / len(latencies)
    max_ping = max(latencies)
    print(f"Benchmark Results: {len(latencies)} reqs, {avg_ping*1000:.1f}ms avg, {max_ping*1000:.1f}ms max | WS: {frames} sent, {results} recv")
    
    async with httpx.AsyncClient() as client:
        await client.post("http://localhost:8000/api/v1/attendance/session/end", headers={"Authorization": f"Bearer {token}"})

if __name__ == "__main__": asyncio.run(main())
