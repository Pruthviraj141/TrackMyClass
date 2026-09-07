# The Visava Advanced Deployment & Debugging Masterclass

This is not a generic deployment guide. This is a hyper-specific, advanced technical log of every major production-breaking bug we encountered while deploying the Visava React/Go/Node stack to AWS EC2, and the exact architectural strict rules to prevent them in future apps.

---

## 1. The GitHub Actions EC2 "Dirty State" Crash
**The Symptom:** CI/CD deployment runs fine normally, but suddenly starts failing at the `git pull` step with errors like *"Your local changes to the following files would be overwritten by merge."*
**The Root Cause:** A developer SSH'd into the AWS EC2 instance and manually modified files like `docker-compose.yml` or `nginx.prod.conf` to try and quickly fix a bug. 
**The Strict Rule:** NEVER edit files directly on a production EC2 server. EC2 is a dumb mirror of your GitHub `main` branch.

**The Advanced Fix:**
When the CI/CD gets stuck because of a "dirty" EC2 state, you must SSH into the server and forcefully blast away local changes:
```bash
# Execute these on the EC2 server inside the project root:
git fetch origin main
# 1. Destroy any manual file edits
git reset --hard origin/main
# 2. Destroy any untracked or ghost files (like temp test files)
git clean -fd
```
*After executing this, your GitHub Action pipeline will successfully run again.*

---

## 2. The React Vite Environment Variable TypeScript Trap 
**The Symptom:** Your app runs locally with `npm run dev`, but fails in the Docker build step or `npm run build` because of environment variables.
**The Root Cause:** Node.js uses `process.env`. Vite uses `import.meta.env`. But if you just type `import.meta.env.VITE_API_URL`, the strict TypeScript compiler will throw:
> *"Property 'env' does not exist on type 'ImportMeta'"*

**The Strict Rule:** For Vite to allow `import.meta.env` without failing the TypeScript build, you MUST explicitly tell the TypeScript compiler about Vite's client types.

**The Advanced Fix:**
You must add `"vite/client"` to your `tsconfig.app.json` (or `tsconfig.json`) compilerOptions:
```json
// tsconfig.app.json
{
  "compilerOptions": {
    "types": ["vite/client"]
  }
}
```
*Without this exact configuration, your automated Docker production builds will fail even if it works perfectly in your local browser.*

---

## 3. The "White Screen of Death" & Mixed Content WebSocket Crash
**The Symptom:** App loads fine on local PC, but when accessed via mobile phone on `https://visava.work.gd`, the screen is completely blank white.
**The Root Cause:** Mobile browsers have extreme security restrictions. Our web socket was hardcoded to `ws://localhost:8081`. 
1. `localhost` does not exist on another person's phone.
2. An `https://` website connecting to an insecure `ws://` port throws a **FATAL Mixed Content Security Error**.
3. Any fatal unhandled JS error in React causes the entire Virtual DOM to unmount, resulting in a blank white screen.

**The Strict Rule:** Never hardcode ports or IPs in production frontend code. Always derive them dynamically from the browser's domain.

**The Advanced Fix:**
*Step 1: Dynamic Protocol Switching*
```typescript
// frontend/src/services/websocket.ts
const hostname = window.location.hostname;
// If the page is running on HTTPS, force WSS (Secure WebSockets). Otherwise, use WS.
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
// Use the Nginx reverse proxy endpoint `/ws/location` not the raw container port
const wsUrl = `${protocol}//${hostname}/ws/location`;
```
*Step 2: Nginx Web-Socket Upgrading*
Nginx must be explicitly told to allow continuous WebSocket traffic on that route:
```nginx
location /ws/location {
    proxy_pass http://geo-service:8081; # Route to internal Docker bridge
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade; # Required for WS
    proxy_set_header Connection "upgrade";  # Required for WS
    proxy_set_header Host $host;
}
```
*Step 3: The React Error Boundary*
Always wrap `main.tsx` in a `<ErrorBoundary>` component. If a fatal crash does happen, it catches it and renders a red UI error box instead of a blank screen, allowing you to actually see what went wrong on the mobile device.

---

## 4. Vapi Webhook Transition: Ngrok to AWS Bridge
**The Symptom:** Vapi AI agent claims it cannot search the database or hallucinate errors.
**The Root Cause:** During local dev, Vapi tools were hooked to an `ngrok` URL (e.g., `https://alfalfa-demo.ngrok.dev/api/v1/voice/tools`). Once deployed to AWS, the container port `4000` is hidden behind AWS security groups and Docker internal networks. Vapi fails to reach it.

**The Strict Rule:** Only expose Port 80 and 443 to the internet. Webhooks must be reverse-proxied by Nginx to the internal Docker container name.

**The Advanced Fix:**
You must update the Vapi Tool MCP Server Config to the production domain (e.g. `https://visava.work.gd/api/v1/voice/tools`), AND map that route in Nginx pointing to the internal container DNS (`voice-agent`):
```nginx
# nginx.prod.conf
location /api/v1/voice {
    # Nginx intercepts this traffic natively over HTTPS, 
    # decrypts it, and forwards it instantly to port 4000
    proxy_pass http://voice-agent:4000;
    proxy_set_header Host $host;
}
```

---

## 5. Defensive Node.js Production Architecture
**The Symptom:** You pass around an EC2 URL on Reddit or HackerNews and your backend crashes instantly due to automated bot brute-forcing. 
**The Root Cause:** Default Express.js accepts unlimited connections. Small AWS EC2 instances (like `t2.micro` or `t3.small`) will exhaust memory and CPU if spammed. 

**The Strict Rule:** Never deploy a naked Express app to the internet without a global Rate Limiter.

**The Advanced Fix:**
```typescript
import rateLimit from 'express-rate-limit';

export const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minute window
  max: 100, // Absolutely limit to 100 requests per IP per window
  message: 'Too many requests, please try again later.',
  standardHeaders: true, // Send RateLimit-* headers to browser
  legacyHeaders: false, // Drop X-RateLimit-* old headers to save bandwidth
});

// Applied globally in index.ts before ANY routes
app.use(globalLimiter); 
```

---

## 6. Space Exhaustion on EC2 Linux Disks
**The Symptom:** GitHub Actions deploy fails with `No space left on device`.
**The Root Cause:** Every time `docker compose build` runs via CI/CD, it compiles a massive multi-gigabyte overlay filesystem. Over 30 deployments, your EC2's 8GB or 30GB EBS drive completely fills up with dangling, unused Docker images.

**The Strict Rule:** CI/CD must clean up its own garbage during every deployment loop.

**The Advanced Fix:**
At the end of your GitHub Actions SSH script, always enforce image pruning. Include the `-f` flag so it doesn't pause waiting for user input on the remote server:
```bash
# Inside deploy.yml action
docker system prune -af --volumes
```
This forces Docker to delete every image, container, network, and volume that is not currently tied to a running container, maintaining your EC2 disk perfectly at 10-15% capacity permanently.
