import asyncio
import aiohttp
import time
import argparse

async def fetch(session, url, headers):
    start = time.perf_counter()
    async with session.get(url, headers=headers) as response:
        await response.read()
        return time.perf_counter() - start, response.status

async def main(concurrency, duration, url, token):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    print(f"Starting API Load Test: {concurrency} users, {duration} seconds against {url}")
    
    async with aiohttp.ClientSession() as session:
        end_time = time.time() + duration
        latencies = []
        status_map = {}
        
        async def worker():
            while time.time() < end_time:
                try:
                    lat, status = await fetch(session, url, headers)
                    latencies.append(lat)
                    status_map[status] = status_map.get(status, 0) + 1
                except Exception as e:
                    status_map["error"] = status_map.get("error", 0) + 1
                    
        tasks = [asyncio.create_task(worker()) for _ in range(concurrency)]
        await asyncio.gather(*tasks)

        if not latencies:
            print("No successful requests.")
            return

        latencies.sort()
        count = len(latencies)
        print(f"\n--- Results ---")
        print(f"Total Requests: {count} ({count/duration:.2f} rps)")
        print(f"Status Codes: {status_map}")
        print(f"P50: {latencies[int(count * 0.50)]*1000:.2f} ms")
        print(f"P95: {latencies[int(count * 0.95)]*1000:.2f} ms")
        print(f"P99: {latencies[int(count * 0.99)]*1000:.2f} ms")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", type=int, default=10, help="Concurrency")
    parser.add_argument("-t", type=int, default=10, help="Duration (sec)")
    parser.add_argument("--url", type=str, default="http://localhost:8000/api/v1/diagnostics/metrics")
    parser.add_argument("--token", type=str, default="")
    args = parser.parse_args()
    asyncio.run(main(args.c, args.t, args.url, args.token))
