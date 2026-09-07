# PERFORMANCE BASELINE

Based on audits and metrics mapped from `scripts/benchmark.py`.

## Infrastructure Configuration
- **Hardware Profile**: Dependent on target EC2 layout (e.g. `t3.large`), currently executed locally utilizing underlying CPU architectures (no local GPUs hooked into PyTorch container scopes). 
- **DB Binding**: SQLite Fallback vs Firebase Firestore.

## API Profile
- **Request Latency (`POST /mark-attendance`)**: High. Dependent on Tensor allocations per bound frame.
- **Error Rates**: None observed in stable network conditions, but prone to timeout dropouts over shaky 3G/4G browser networks because the payload relies heavily on synchronous file encoding.

## Recognition Pipeline Latency
*(Simulated limits derived from CPU processing models)*
- **Model Initialization**: Multi-second blocker. Handled efficiently via `@asynccontextmanager (lifespan)` so end-users don't experience caching delays.
- **Face Detection (MTCNN)**: ~40ms - 80ms per frame.
- **Embedding Generation (FaceNet)**: ~60ms - 150ms per frame.
- **Vector Matching**: `<1ms` scaled up to `5000+` students thanks to in-memory vectorized mapping (`vector @ Cache`).
- **Temporal Tracking**: `<1ms` standard dict caching.
- **Database Persistence**: `1-10ms` for SQLite local IO.

## Scalability & Capacity Status
- **Current Max FPS**: ~6 FPS maximum pipeline execution synchronously before CPU bottlenecks on standard deployments.
- **Scale Problem**: Single frame iteration (`for i in tensors: embed...`) scales *O(F)* per face detected adding cumulative hundreds of milliseconds per Face. 
- **Recommendation**: GPU invocations inside Docker builds paired with proper batch Tensors (`[N, C, H, W]`).
