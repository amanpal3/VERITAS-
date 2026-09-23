# VERITAS Cloud Deployment & Production Guide

This guide provides complete instructions for deploying the VERITAS platform to production using **Render** and configuring monitoring, database connections, and environment variables.

---

## 1. Deployment Architecture on Render

```
                             [Judges / Users Browser]
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
     [Render Static Site]                             [Render Web Service]
       veritas-frontend                                 veritas-backend
    (React / Vite Production)                       (FastAPI / Uvicorn API)
                 |                                             |
                 | API Calls (/api/v1/*)                       |
                 +--------------------------------------------->
                                                               |
                                            +------------------+------------------+
                                            |                                     |
                                            v                                     v
                                   [Neo4j AuraDB Cloud]                  [In-Memory NetworkX]
                                  (Primary Managed Graph)               (Fail-Safe Demo Graph)
```

---

## 2. Blueprint Configuration: `render.yaml`

The project root contains `render.yaml` which automatically declares both services for Render's Infrastructure-as-Code blueprint engine:

```yaml
services:
  # Backend API Service
  - type: web
    name: veritas-backend
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: uvicorn backend.app.main:app --host 0.0.0.0 --port 10000
    healthCheckPath: /api/v1/health
    envVars:
      - key: NEO4J_URI
        sync: false
      - key: NEO4J_USER
        sync: false
      - key: NEO4J_PASSWORD
        sync: false
      - key: CORS_ORIGINS
        value: '["https://veritas-frontend.onrender.com", "http://localhost:5173"]'
      - key: SENTRY_DSN
        sync: false
      - key: ENVIRONMENT
        value: production
      - key: USE_IN_MEMORY_FALLBACK
        value: "true"

  # Frontend Static Site
  - type: web
    name: veritas-frontend
    env: static
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: frontend/dist
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
    envVars:
      - key: VITE_API_BASE_URL
        value: https://veritas-backend.onrender.com/api/v1
```

---

## 3. Environment Variables Reference

| Variable Name | Service | Required? | Default / Example | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `NEO4J_URI` | Backend | Optional | `neo4j+s://xxxx.databases.neo4j.io` | Connection URI for Neo4j AuraDB instance |
| `NEO4J_USER` | Backend | Optional | `neo4j` | Database username |
| `NEO4J_PASSWORD`| Backend | Optional | `SecurePassword123` | Database access password |
| `USE_IN_MEMORY_FALLBACK` | Backend | Yes | `true` | Allows instant fallback to NetworkX if Neo4j is offline |
| `CORS_ORIGINS` | Backend | Yes | `["https://veritas-frontend.onrender.com"]` | Authorized origin whitelist for cross-origin requests |
| `SENTRY_DSN` | Backend | Optional | `https://xxxx@sentry.io/yyyy` | Sentry DSN for live crash reporting & performance |
| `ENVIRONMENT` | Backend | Yes | `production` | Environment indicator |
| `VITE_API_BASE_URL` | Frontend | Yes | `https://veritas-backend.onrender.com/api/v1` | Backend API base path queried by Cytoscape & Axios |

---

## 4. Neo4j Cloud Database Setup (Neo4j AuraDB)

1. Sign up for a free cloud graph database at [https://neo4j.com/cloud/aura/](https://neo4j.com/cloud/aura/).
2. Create an **AuraDB Free** instance.
3. Download the credentials file containing the **Connection URI**, **Username** (`neo4j`), and **Generated Password**.
4. In Render Dashboard $\to$ `veritas-backend` $\to$ Environment, add `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD`.
5. Run the loader script to seed demo records into AuraDB:
   ```bash
   python scripts/load_neo4j.py
   ```

---

## 5. Sentry Production Error Tracking

VERITAS integrates **Sentry** for production monitoring to ensure any unexpected runtime exception during judging is logged with complete stack traces.

- **Backend Integration**: In `backend/app/main.py`, Sentry initializes automatically if `SENTRY_DSN` is present.
- **Fail-Safe Logging**: If `SENTRY_DSN` is not provided, the system gracefully continues logging to stdout without throwing errors.
- **Alerts**: Critical endpoint failures trigger immediate notifications so issues can be remediated before the live demo.

---

## 6. Pre-Flight Presentation Checklist (T - 2 Hours to Demo)

Run these 10 sanity checks before presenting to judges:

- [ ] **1. Backend Health Check**: Navigate to `https://veritas-backend.onrender.com/api/v1/health` — must return `{"status": "healthy"}`.
- [ ] **2. Swagger Docs Accessible**: Open `https://veritas-backend.onrender.com/docs` to verify API documentation renders cleanly.
- [ ] **3. Graph Payload Verification**: Query `/api/v1/graph` to confirm nodes and edges are populated.
- [ ] **4. Frontend Live Check**: Navigate to `https://veritas-frontend.onrender.com` in an incognito window.
- [ ] **5. Canvas Rendering**: Verify the Cytoscape graph canvas initializes, displays colored nodes, and supports zoom and pan.
- [ ] **6. Path Highlighter Test**: Test "Find Connection" between two demo suspects to confirm the glowing path appears.
- [ ] **7. Evidence Modal Check**: Click any edge; verify source FIR/CDR snippet appears in the drawer.
- [ ] **8. Centrality Leaderboard**: Open the Analytics tab to confirm PageRank and Betweenness charts populate.
- [ ] **9. Community Partitioning**: Confirm distinct colors indicate separated sub-gangs.
- [ ] **10. Fallback Active**: Ensure `USE_IN_MEMORY_FALLBACK=true` so that network hiccups never crash the live presentation.
