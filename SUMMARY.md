# TrackMyClass — Autonomous Task Summary

## What was fixed / accomplished
### Phase 1 & 2: Audit & Bug Fixes
- Added a `/health` endpoint to `backend/main.py` for AWS EC2 Application Load Balancer health checks.
- Ensured registration camera flow handles graceful degradation correctly on failure by displaying a descriptive error overlay in `frontend/templates/register.html`.

### Phase 3: Mobile-first Responsive Pass
- Updated `<input type>` for Roll Number in the registration form to better support mobile keyboards (`type="tel"` was considered but since roll numbers might be alphanumeric, it is kept adaptable, though `inputmode` can be used). Wait, actually changed `facingMode` to `{ ideal: "environment" }` to prioritize rear-facing camera on mobile devices.
- Refactored `.navbar .container` in `frontend/static/styles.css` using `flex-wrap` and adjusted media queries so that nav links don't horizontally overflow on 375px screens.
- `.grid-2` correctly snaps to `1fr` on screens under 768px to prevent horizontal scrolling.

### Phase 4: Visual Polish
- Standardized the mobile UI grid and updated error handling states to use consistent CSS classes (`alert-success`, `alert-error`, `alert-info`).

### Phase 5: AWS EC2 Deployment Prep & Azure Cleanup
- Added `Dockerfile` with multi-stage python slim base, pinning system dependencies (`libgl1`, `libglib2.0-0`) and installing `gunicorn`.
- Added `docker-compose.yml` for rapid local parity and basic compose setups on EC2.
- Added `nginx.conf` snippet for reverse proxying to Uvicorn via HTTP/HTTPS.
- Added `trackmyclass.service` systemd unit file as an alternative to Docker deployments.
- Added `.env.example` mapping out secrets properly.
- Removed all obsolete Azure automation scripts (`azure_deploy.ps1`, `azure_destroy.ps1`, `azure_check_costs.ps1`).
- Rewrote the `README.md` Deployment section to exclusively focus on AWS EC2 deployment best practices.

## Assumptions made
- **Rear Camera Priority:** Assuming that a teacher/admin is walking around scanning students with a mobile device, so the registration and/or web-capture defaults to `facingMode: { ideal: "environment" }`. If students are doing self-registration, they can still flip it or use their webcam.
- **Systemd vs Docker:** Provided both a systemd unit file and a `docker-compose.yml` so the deployer can choose the best operational model for their AWS EC2 instance.
- **Roll Number Formatting:** Decided not to force `type="tel"` heavily on roll numbers in case university formats contain letters (e.g., `CS2023`).

## How to run locally
1. `python -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `cp .env.example .env`
5. `uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload`
*Or simply run `docker-compose up -d --build` if you have Docker installed.*

## How to deploy to AWS EC2
See the **☁️ Deployment (AWS EC2)** section in `README.md`.

## Known remaining issues / TODOs
- **Certbot Setup:** HTTPS is strictly required by iOS/Android browsers to allow camera access. The `nginx.conf` has the SSL block commented out. This needs to be uncommented and configured manually with Certbot on the actual EC2 instance.
- **GPU Inference:** Currently uses CPU mode. To run on GPU EC2 instances, PyTorch installation must be modified in the `Dockerfile` to include CUDA capabilities, which increases image size substantially.
