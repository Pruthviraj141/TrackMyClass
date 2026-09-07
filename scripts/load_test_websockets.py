import asyncio
import websockets
import time
import argparse

async def connection_worker(url, token, session_id, duration, fps_limit=10):
    ws_url = f"{url}/{session_id}?token={token}"
    fake_frame = b"ffd8ffe000104a46494600010101006000600000" # minimal valid looking header
    end_time = time.time() + duration
    frame_delay = 1.0 / fps_limit
    
    try:
        async with websockets.connect(ws_url) as ws:
            while time.time() < end_time:
                s = time.perf_counter()
                await ws.send(fake_frame)
                await asyncio.sleep(max(0, frame_delay - (time.perf_counter() - s)))
            return "SUCCESS"
    except Exception as e:
        return f"ERROR: {e}"

async def main(concurrency, duration, url, token):
    print(f"Starting WS Load Test: {concurrency} clients, {duration} sec at 10FPS Limit.")
    tasks = [
        asyncio.create_task(connection_worker(url, token, f"SESS_{i}", duration)) 
        for i in range(concurrency)
    ]
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    
    success = results.count("SUCCESS")
    errors = len(results) - success
    
    print(f"\n--- WS Results ---")
    print(f"Total connections tested: {concurrency}")
    print(f"Successful persistence: {success}")
    print(f"Errors via overload: {errors}")
    print(f"Total time elapsed: {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", type=int, default=5, help="Concurrency")
    parser.add_argument("-t", type=int, default=10, help="Duration (sec)")
    parser.add_argument("--url", type=str, default="ws://localhost:8000/api/v1/ws/monitor")
    parser.add_argument("--token", type=str, default="")
    args = parser.parse_args()
    asyncio.run(main(args.c, args.t, args.url, args.token))
