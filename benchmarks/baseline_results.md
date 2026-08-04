# Phase 0: Baseline Benchmark Results

## 1. Initialization
- **Model Load Time (MTCNN + FaceNet):** 24.21 seconds
  *This represents the cold-start delay when the FastAPI server first boots. Singleton caching prevents this on subsequent requests.*

## 2. Detection Latency (MTCNN)
- **Mean Latency:** 139.84 ms
- **Median Latency:** 124.40 ms
- **95th Percentile:** 203.40 ms
  *Time taken to locate a face in a frame and crop it.*

## 3. Embedding Latency (FaceNet)
- **Mean Latency:** 47.44 ms
- **Median Latency:** 44.92 ms
- **95th Percentile:** 61.57 ms
  *Time taken to convert a cropped face into a 512-d vector.*

## 4. End-to-End Latency & FPS (1 Face)
- **Total Latency (per frame):** 187.29 ms
- **Theoretical Max FPS:** 5.3 FPS
  *Combined detection, embedding, and matching. This represents the pipeline's real-time capability.*

## 5. Matching Latency at Scale (Simulated)
| Registered Students | Mean Math Time (ms) |
|---------------------|---------------------|
| 10 | 0.0157 ms |
| 100 | 0.0162 ms |
| 1000 | 2.0355 ms |
| 5000 | 0.5331 ms |

  *Because matching relies on vectorized Numpy operations in RAM, scaling to thousands of students adds virtually zero overhead.*

## 6. Memory Footprint
- **RAM Used (Models Loaded):** 552.43 MB
  *Includes Python overhead, FastAPI, and PyTorch weights loaded into RAM.*

## 7. Accuracy Baseline
- **True Positive Rate:** 100.0%
- **False Positive Rate:** 0.0%
  *Evaluated using a synthetic similarity test at a strict confidence threshold of 0.8. Sample size limitation: Evaluated on 20 pairs because large local dataset is not present.*

## 7. Concurrency Baseline (FastAPI Endpoint)
| Concurrent Clients | Requests | Success | Errors | Mean Latency (ms) | Max Latency (ms) | Total Time (s) |
|--------------------|----------|---------|--------|-------------------|------------------|----------------|
| 1 | 20 | 20 | 0 | 700.04 | 898.41 | 14.00 |
| 5 | 20 | 20 | 0 | 2715.09 | 2876.88 | 10.89 |
| 10 | 20 | 20 | 0 | 5673.40 | 6192.46 | 11.42 |

  *This load test sends a base64 frame to the `/api/mark-attendance` endpoint.* *As concurrency increases, the CPU-bound deep learning tasks (MTCNN + FaceNet) become the bottleneck, causing latency to degrade.* 

