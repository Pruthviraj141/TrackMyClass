import asyncio
import time
import argparse
import aiohttp
import websockets

async def ws_worker(url, duration):
    end = time.time() + duration
    frame = b"ffd8ffe000104a46494600010101006000600000"
    connected = 0
    try:
        async with websockets.connect(url) as ws:
            connected = 1
            while time.time() < end:
                await ws.send(frame)
                await asyncio.sleep(0.1)  # 10 FPS
    except:
        pass
    return connected

async def http_worker(url, duration):
    end = time.time() + duration
    calls = 0
    try:
        async with aiohttp.ClientSession() as session:
            while time.time() < end:
                async with session.get(url) as r:
                    await r.read()
                    calls += 1
    except:
        pass
    return calls

async def main(duration):
    print(f"Starting Mixed Workload Soak Test for {duration} seconds.")
    ws_tasks = [asyncio.create_task(ws_worker("ws://localhost:8000/api/v1/ws/monitor/demo", duration)) for _ in range(5)]
    http_tasks = [asyncio.create_task(http_worker("http://localhost:8000/api/v1/diagnostics/metrics", duration)) for _ in range(20)]
    
    start_time = time.time()
    await asyncio.gather(*(ws_tasks + http_tasks))
    
    print("Test Completed natively testing mixed concurrency.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", type=int, default=10, help="Duration")
    args = parser.parse_args()
    asyncio.run(main(args.t))
