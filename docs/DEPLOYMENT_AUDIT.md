# Deployment Baseline Audit

An audit of the current deployment pipeline and infrastructure architecture based on `Dockerfile`, `docker-compose.yml`, `nginx.conf`, and `trackmyclass.service`.

## Components
1. **Dockerfile**: Leverages a python slim base image. Pins specific system dependencies (`libgl1`, `libglib2.0-0` required for OpenCV). Uses Gunicorn with Uvicorn workers for production CPU deployment. Wait - PyTorch requires massive amounts of data so caching layers are not cleanly isolated here causing huge build sizes.
2. **docker-compose.yml**: Maps port `8000:8000`. Loads `.env` file directly. Maps a local volume for SQLite persistence (`./backend/database:/app/backend/database`). Has `restart: always` set.
3. **Nginx/Reverse Proxy**: `nginx.conf` exists for routing HTTP/HTTPS directly into Uvicorn/Gunicorn. Heavily relied on for mobile `getUserMedia` camera constraints (HTTPS is strictly required).
4. **systemd (trackmyclass.service)**: Alternate raw execution method for Linux instances without Docker overhead.

## Architecture
Browser -> Internet -> AWS EC2 (Target environment defined in README) -> Nginx (Port 80/443 SSL termination) -> Docker Container (Port 8000) -> Uvicorn Workers -> FastAPI.

## Deficiencies & Weaknesses
- **Stateful Persistence**: The SQLite Volume relies on a direct flat file map. Moving to AWS ECS or Kubernetes would drop database state. Cloud Firebase is the intended future-proof route.
- **CI/CD Missing**: No `.github/workflows` actively automating tests or container registry pushes.
- **Static Assets**: Frontend build (`dist/`) isn't explicitly hosted via Nginx static maps, it relies on FastAPI's `StaticFiles` which is CPU overhead.
- **Environment Variables**: No strict validation is present forcing `.env` schemas. If `.env` is incomplete, the system will start unreliably.
