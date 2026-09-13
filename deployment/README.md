# Deployment Guide: Ultimate Travel MCP Server

This directory contains containerization and cloud deployment manifests to deploy the Ultimate Travel MCP Server to modern cloud hosting platforms.

---

## 1. Supported Deployment Targets

| Platform | Manifest File | Typical Setup Time | Free / Starter Tier Available? |
| :--- | :--- | :--- | :--- |
| **Local Docker** | `Dockerfile`, `docker-compose.yml` | 1 minute | Yes (100% free / local) |
| **Railway** | `deployment/railway.json` | 3 minutes | Yes ($5 monthly trial credit) |
| **Render** | `deployment/render.yaml` | 3 minutes | Yes (Free web service tier) |
| **Fly.io** | `deployment/fly.toml` | 3 minutes | Yes (Hobby allowance) |
| **Google Cloud Run** | `deployment/cloudrun.yaml` | 5 minutes | Yes (2M free requests/mo) |

---

## 2. Deploying Locally with Docker Compose

To run the container locally on port 8001:

```bash
# Build and start container in background
docker compose up -d --build

# Verify health status
curl http://localhost:8001/health

# Check logs
docker compose logs -f

# Stop container
docker compose down
```

---

## 3. Deploying to Cloud Platforms

### A. Railway
1. Push your repository to GitHub.
2. In Railway Dashboard: **New Project** > **Deploy from GitHub Repo**.
3. Railway automatically detects `deployment/railway.json` and builds from `Dockerfile`.
4. In Railway **Variables**, add:
   - `TRAVEL_MCP_API_KEY`: Generate a random secret (e.g. `openssl rand -hex 24`).
   - `TRAVEL_MCP_AUTH_REQUIRED`: `true`.

### B. Render
1. In Render Dashboard: **New** > **Blueprint**.
2. Select your repository. Render reads `deployment/render.yaml`.
3. Render automatically provisions the service and auto-generates a secure `TRAVEL_MCP_API_KEY`.

### C. Fly.io
```bash
fly launch --config deployment/fly.toml
fly secrets set TRAVEL_MCP_API_KEY="your-random-secret-key"
fly deploy
```

### D. Google Cloud Run
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ultimate-travel-mcp:latest
gcloud run deploy ultimate-travel-mcp \
  --image gcr.io/YOUR_PROJECT_ID/ultimate-travel-mcp:latest \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars="TRAVEL_DEFAULT_MODE=offline,TRAVEL_MCP_AUTH_REQUIRED=true"
```

---

## 4. Health Checks & Monitoring

The container exposes two standardized probe endpoints:
- `GET /health`: Liveness probe (HTTP 200 `{"status": "healthy"}`).
- `GET /ready`: Readiness probe (HTTP 200 `{"status": "ready"}`).
- `GET /version`: Metadata probe (HTTP 200 with server & MCP spec versions).

Health probes require no authentication and never leak backend configuration secrets.
