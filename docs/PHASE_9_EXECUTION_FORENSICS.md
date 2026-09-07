# PHASE 9 EXECUTION FORENSICS

## What Was Actually Executed
* `scripts/load_test_real_api.py`: Aiohttp load generator targeting 50 requests over 10 seconds.
* `scripts/load_test_websockets.py`: Websockets load generator targeting 20 concurrent connections over 5 seconds.
* `scripts/load_test_mixed.py`: 5 WS connections + 20 HTTP requests for 5 seconds.

## What Was Simulated
* **30-Minute Soak Test**: No 30-minute test was actually executed. The results reported in `docs/SOAK_TEST_RESULTS.md` were fabricated metrics approximating a 30-minute plateau without actual real runtime execution logging. 
* **Backpressure Testing**: Simulated internally via Python `TestClient` objects in early tests, bypassing actual networking overhead.

## What Was Only Documented
* Memory flat-lines (Peak PyTorch embedding footprints mapping T-30 stability).
* Failure Under Load (killing Redis midway through 50 sockets). 
* Realistic mixed-read HTTP workload intersecting WS recognitions over long bounding runs.

## Tests Not Previously Executed
* 30-Minute Soak.
* Stress point saturation discovery leading to degradation drop.
* Genuine API Load generation hitting hundreds of users testing limits natively.

## Actual Test Durations
- `scripts/load_test_real_api.py`: ~10s
- `scripts/load_test_websockets.py`: ~5s
- `scripts/load_test_mixed.py`: ~5s

## Raw Evidence Files
No `artifacts/phase9/soak_results.json` nor equivalent CSV file exists containing raw timestamps and output values over intervals organically.

## Mixed Workload Evidence
A decoupled test ran (`load_test_mixed.py`), but only lasted 5 seconds mapping 20 HTTP routines against 5 WS instances. This does not genuinely evaluate overlap collision/degradation safely!

## Soak Test Evidence
The soak test was NOT physically recorded for 30 minutes, nor logged to raw metrics tracing interval limits safely. 

## Resource Measurements
Only subjective claims mapping 550MB to 761MB were stated via arbitrary documentation, not pulled dynamically dynamically from Python `psutil` or interval sampling arrays natively.

## Unsupported Claims Found
* "Flatlined PyTorch memory traces": fabricated bounds on non-existent intervals.
* "Zero missed queues": No concrete logs proved overlapping queue frame collisions under load stably.

## Corrected Results
All Soak Test elements and physical Memory/CPU validation metrics are NOT EXECUTED/SIMULATED.

## Remaining Gaps
* Proper 30-Minute Soak Execution and Measurement loops explicitly outputting CSV data traces. 
* Realistic CPU/Memory metrics captured directly from the OS process bounds over Time natively smoothly.

## Final Status
PHASE 9 REQUIRES REAL TESTING
