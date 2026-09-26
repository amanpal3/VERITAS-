# VERITAS — Production Deployment Guide (Render.com)

> **Platform**: [Render.com](https://render.com) (Infrastructure as Code via `render.yaml`)  
> **Repository**: `https://github.com/amanpal3/VERITAS-`  
> **Status**: Verified & Ready for Blueprint Deployment

---

## 1. Architecture Overview

VERITAS deploys as two decoupled services managed within a single unified Render Blueprint:

```
┌─────────────────────────────────────────────────────────────┐
│                         RENDER.COM                          │
│                                                             │
│   ┌──────────────────────────┐   JSON API   ┌───────────┐  │
│   │ veritas-frontend         │ ───────────> │ veritas-  │  │
│   │ (Vite Static Site)       │              │ backend   │  │
│   │ https://veritas-frontend │              │ (FastAPI) │  │
│   │ .onrender.com            │              │           │  │
│   └──────────────────────────┘              └─────┬─────┘  │
│                                                   │         │
│                                      ┌────────────┴─────┐   │
│                                      │ In-Memory        │   │
│                                      │ NetworkX Engine  │   │
│                                      │ (or Neo4j Aura)  │   │
│                                      └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

1. **`veritas-backend` (Python Web Service)**:
   * **Runtime**: Python 3.11+
   * **Build Command**: `pip install -r backend/requirements.txt`
   * **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port 10000`
   * **Features**: Automatic NetworkX graph hydration with 29 entities, 33 evidentiary links, Louvain modularity clustering, and PageRank/Betweenness ranking. Graceful fallback if external Neo4j is not attached.

2. **`veritas-frontend` (Static Site)**:
   * **Build Command**: `cd frontend && npm install && npm run build`
   * **Publish Directory**: `frontend/dist`
   * **Routing**: Automated rewrite rule (`/* -> /index.html`) for React SPA deep linking.

---

## 2. Step-by-Step Deployment Instructions

### Step 1: Commit and Push Changes to GitHub

Ensure your local branch is committed and pushed to GitHub:

```bash
git add .
git commit -m "feat: complete UI/UX, Home page, TeamMETX footer, and Render blueprint"
git checkout main
git merge devlop
git push origin main
```

---

### Step 2: Create a Blueprint on Render

1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. In the top navigation, click **New +** and select **Blueprint**.
3. Connect your GitHub account and select the **`amanpal3/VERITAS-`** repository.
4. Select the branch you want to deploy (e.g., `devlop` or `main`).
5. Render will automatically detect [`render.yaml`](../render.yaml) at the repository root and display the two configured services:
   * `veritas-backend`
   * `veritas-frontend`
6. Click **Apply**.

---

### Step 3: Configure Environment Variables

#### For `veritas-frontend`:
* Once the backend service starts, copy its public URL (e.g., `https://veritas-backend.onrender.com`).
* In Render Dashboard, navigate to **`veritas-frontend`** ➔ **Environment**.
* Set:
  ```env
  VITE_API_BASE_URL=https://veritas-backend.onrender.com/api/v1
  ```
* Click **Save Changes** and trigger a manual redeploy.

#### For `veritas-backend` (Optional):
* **Default zero-config mode**: If no database variables are provided, VERITAS automatically operates on its high-speed in-memory NetworkX engine with full analytics support.
* **External Neo4j Aura (Optional)**:
  ```env
  NEO4J_URI=neo4j+s://<your-database-id>.databases.neo4j.io
  NEO4J_USER=neo4j
  NEO4J_PASSWORD=<your-database-password>
  ```
* **Sentry Error Tracking (Optional)**:
  ```env
  SENTRY_DSN=https://<public_key>@o<org_id>.ingest.sentry.io/<project_id>
  ```

---

## 3. Post-Deployment Verification Checklist

Once Render marks both services as **Live**:

1. **Verify Backend Health**:
   Open in your browser:
   ```
   https://veritas-backend.onrender.com/api/v1/health
   ```
   Expected response:
   ```json
   {
     "status": "healthy",
     "service": "veritas-api",
     "version": "1.0.0",
     "graph_backend": "in-memory-networkx",
     "total_nodes": 29,
     "total_edges": 33
   }
   ```

2. **Verify Interactive API Docs**:
   Open `https://veritas-backend.onrender.com/docs` to test Swagger UI live.

3. **Verify Frontend UI**:
   Open `https://veritas-frontend.onrender.com/`:
   * Confirm the **Bureau Landing Page** loads with active operation stats.
   * Navigate to **Overview Dashboard** (`/dashboard`).
   * Test the **Network Explorer** (`/network`) canvas and path finder.
   * Verify deep linking (refresh page on `/entities` or `/analytics` — should not 404).
   * Confirm custom cursor reticle and footer badges are active.

---

## 4. Continuous Deployment (CI/CD)

Whenever you push new commits to your connected GitHub branch, Render automatically rebuilds and redeploys both the backend and frontend services without downtime.
