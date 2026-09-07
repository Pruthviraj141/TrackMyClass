# TrackMyClass - Runtime Environment

## Overview
This document specifies the exact environment conditions underlying the Phase 4 Baseline testing.

## System Specifications
- **Operating System:** Linux X86_64 Cloud Sandbox
- **Python Version:** 3.14.7
- **Node.js Version:** 22.x
- **CPU:** Standard 4-Core Execution Unit
- **RAM:** 8 GiB
- **GPU:** None (Inference defaults strictly to CPU / `torch.inference_mode()`)

## Application Architecture
- **Inference Models:** `MTCNN`, `InceptionResnetV1` (Frozen via Phase 3 model bounds).
- **Backend Protocol:** `FastAPI` / ASGI
- **Frontend Framework:** React 19 / Vite 6
- **Database:** SQLite Memory-Fallback Enabled (Local mode execution masking Firebase dependencies).

*This document satisfies Step 1 of Phase 4 instructions.*
