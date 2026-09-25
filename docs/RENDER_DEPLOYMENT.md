# Deploying MediKiosk Backend to Render

This guide provides step-by-step instructions to deploy the **MediKiosk FastAPI Backend** and its database to [Render.com](https://render.com).

---

## Architecture Overview on Render

- **Backend Web Service**: Python 3 running FastAPI with Uvicorn.
- **Database**: Render Managed PostgreSQL (Free Tier) or local SQLite (`aiosqlite`).
- **Connection to Frontend**: Vercel frontend connects via the environment variable `VITE_API_BASE_URL`.

---

## Step 1: (Recommended) Create PostgreSQL Database on Render

1. Log in to [dashboard.render.com](https://dashboard.render.com/).
2. Click **New +** in the top navigation and select **PostgreSQL**.
3. Configure your database:
   - **Name**: `medikiosk-db`
   - **Database**: `medikiosk_db`
   - **User**: `medikiosk`
   - **Region**: Choose the region closest to you (e.g., *Singapore* or *Oregon*).
   - **Plan**: Select **Free**.
4. Click **Create Database**.
5. Once created, scroll down to **Connections** and copy the **Internal Database URL** (e.g. `postgres://medikiosk:...@dpg-...-a/medikiosk_db`).
   > *Note:* The backend automatically formats `postgres://` into `postgresql+asyncpg://` for async SQLAlchemy.

---

## Step 2: Deploy the Backend Web Service

1. On your Render dashboard, click **New +** and select **Web Service**.
2. Select **Build and deploy from a Git repository** and connect your GitHub repository (`Skit-025/AnudVegam`).
3. Fill in the service configuration:
   - **Name**: `medikiosk-backend`
   - **Region**: Select the same region as your database.
   - **Branch**: `main`
   - **Root Directory**: `backend` *(Important: Must be `backend`)*
   - **Runtime**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type**: Select **Free**.

---

## Step 3: Add Environment Variables in Render

In the same Web Service creation page (or under **Environment** tab):

| Variable Name | Example Value | Description |
|---|---|---|
| `DATABASE_URL` | *(Pasted from Step 1)* | Render internal Postgres connection URL. If omitted, it defaults to SQLite. |
| `ENVIRONMENT` | `production` | Production environment flag |
| `DEBUG` | `false` | Disable debug logs |
| `SECRET_KEY` | `medikiosk-production-super-secret-key-32-chars-long` | Random 32+ character secret string |

Click **Create Web Service**.

---

## Step 4: Verify Deployment

Render will pull the code, install dependencies, and start Uvicorn. Once the status shows **Live**:

1. Click your Render URL (e.g., `https://medikiosk-backend.onrender.com`).
2. Test the API docs:
   - Open `https://medikiosk-backend.onrender.com/docs` (Swagger UI).
3. Test the health endpoint:
   - Open `https://medikiosk-backend.onrender.com/health` (should return `{"status": "ok"}`).

---

## Step 5: Link Render Backend to Vercel Frontend

1. Go to your [Vercel Dashboard](https://vercel.com/dashboard).
2. Select your `frontend` project.
3. Navigate to **Settings** > **Environment Variables**.
4. Add a new variable:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: `https://medikiosk-backend.onrender.com` *(your actual Render URL, without trailing slash)*
5. Go to the **Deployments** tab and click **Redeploy** on the latest deployment so Vite bakes in the new API URL.

---

## (Optional) Deploying AI Microservices

If you want the full AI microservices pipeline active on Render:
- **Dialogue Service**: Create a Web Service with Root Directory `ai-services/dialogue`, Start Command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- **OCR Service**: Create a Web Service with Root Directory `ai-services/ocr`, using Docker (`ai-services/ocr/Dockerfile`).
- **Summarizer Service**: Create a Web Service with Root Directory `ai-services/summarizer`, Start Command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
- In your main backend's Render environment variables, update `DIALOGUE_SERVICE_URL`, `OCR_SERVICE_URL`, and `SUMMARIZER_SERVICE_URL` with their respective internal URLs.
