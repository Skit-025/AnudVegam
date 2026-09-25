# Deploying MediKiosk to Vercel

This repository is pre-configured for one-click deployment on **Vercel**. Both root repository imports and subdirectory deployments (`frontend/`) are supported.

---

## Option 1: Deploy via Vercel Dashboard (GitHub Import)

1. Push your repository to GitHub.
2. Go to [vercel.com/new](https://vercel.com/new) and import your repository.
3. Configure the Project:
   - **Framework Preset**: `Vite` (or `Other` if deploying from root)
   - **Root Directory**: 
     - **Recommended**: Set to `frontend`
     - Alternatively, leave as `./` (the root `vercel.json` and `package.json` will automatically build the frontend).
4. **Environment Variables** (Optional):
   - `VITE_API_BASE_URL`: URL of your deployed FastAPI backend (e.g. `https://your-api.onrender.com` or `https://api.yourdomain.com`).
   - *Note*: If left unset, the frontend will automatically use realistic offline fallback data for seamless demonstrations.
5. Click **Deploy**.

---

## Option 2: Deploy via Vercel CLI

Ensure you have the Vercel CLI installed:
```bash
npm i -g vercel
```

### Deploying directly from frontend (Fastest):
```bash
cd frontend
vercel
```

For production deployment:
```bash
vercel --prod
```

### Deploying from repository root:
```bash
vercel
```
The root `vercel.json` directs Vercel to install dependencies in `frontend/`, run `vite build`, and serve `frontend/dist`.

---

## Features Configured

- **Single Page Application (SPA) Routing**: Rewrites are configured in `vercel.json` (`/.* -> /index.html`) so direct navigation and refreshes on `/doctor`, `/summary`, `/converse`, and `/demo` work seamlessly without 404 errors.
- **Cache Optimization**: Assets in `/assets/*` are configured with long-term immutable caching (`Cache-Control: public, max-age=31536000, immutable`).
- **Lean Deployments**: `.vercelignore` excludes Python backend, virtual environments, SQLite database files, and AI services from the Vercel bundle.
