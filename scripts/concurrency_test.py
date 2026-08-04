import asyncio
import aiohttp
import base64
import time
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sample_img_path = os.path.join(PROJECT_ROOT, "benchmarks", "sample_face.jpg")

async def fetch(session, url, payload):
    start = time.time()
    try:
        async with session.post(url, json=payload) as response:
            await response.read()
            return time.time() - start, response.status
    except Exception as e:
        return time.time() - start, 500

async def bound_fetch(sem, session, url, payload):
    async with sem:
        return await fetch(session, url, payload)

async def run_test(concurrency, num_requests, url, payload):
    sem = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(num_requests):
            task = asyncio.ensure_future(bound_fetch(sem, session, url, payload))
            tasks.append(task)
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        times = [r[0] for r in responses if r[1] == 200]
        errors = len([r for r in responses if r[1] != 200])
        
        return {
            'concurrency': concurrency,
            'total_time': total_time,
            'requests': num_requests,
            'success': len(times),
            'errors': errors,
            'mean_latency': sum(times) / len(times) if times else 0,
            'max_latency': max(times) if times else 0
        }

def run_concurrency_benchmarks():
    with open(sample_img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')
        
    url = "http://localhost:8000/api/mark-attendance"
    payload = {"frame": img_b64}
    
    import requests
    import subprocess
    
    print("Starting FastAPI server...")
    server_process = subprocess.Popen(
        ["uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=PROJECT_ROOT
    )
    time.sleep(10) # wait for models to load
    
    try:
        # Start session
        requests.post("http://localhost:8000/api/session/start", json={"subject_name": "Benchmark Test"})
        
        results = []
        for concurrency in [1, 5, 10]:
            print(f"Running concurrency test with {concurrency} clients...")
            res = asyncio.run(run_test(concurrency, 20, url, payload))
            results.append(res)
            
        # End session
        requests.post("http://localhost:8000/api/session/end")
        
        with open(os.path.join(PROJECT_ROOT, "benchmarks", "baseline_results.md"), "a") as f:
            f.write("## 7. Concurrency Baseline (FastAPI Endpoint)\n")
            f.write("| Concurrent Clients | Requests | Success | Errors | Mean Latency (ms) | Max Latency (ms) | Total Time (s) |\n")
            f.write("|--------------------|----------|---------|--------|-------------------|------------------|----------------|\n")
            for r in results:
                f.write(f"| {r['concurrency']} | {r['requests']} | {r['success']} | {r['errors']} | {r['mean_latency']*1000:.2f} | {r['max_latency']*1000:.2f} | {r['total_time']:.2f} |\n")
            
            f.write("\n  *This load test sends a base64 frame to the `/api/mark-attendance` endpoint.* ")
            f.write("*As concurrency increases, the CPU-bound deep learning tasks (MTCNN + FaceNet) become the bottleneck, ")
            f.write("causing latency to degrade.* \n\n")
            
    except requests.exceptions.ConnectionError:
        print("Server not running. Please start the FastAPI server before running concurrency tests.")
    finally:
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    run_concurrency_benchmarks()
