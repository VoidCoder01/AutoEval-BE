# EvalAI – AI project evaluation
Production-grade, AI-powered project evaluation. Upload a project, the backend analyzes code/docs using OpenAI GPT‑4o, and the frontend visualizes strict, differentiated scores with detailed feedback.

---

## 1) Architecture Overview

```
EvalAI/                   # Frontend (Svelte 5 + Vite + Tailwind) and # Backend (Flask + SQLite)
```

- Backend exposes REST API, handles file uploads, extracts code/docs, chunks large content, calls OpenAI, persists results.
- Frontend provides upload, individual results, and leaderboard views with animations and accessibility.

---

## 2) Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API key with access to `gpt-4o`
- Windows/macOS/Linux

---

## 3) Backend (Flask)

### 3.1 Setup
```bash
cd Eval
python -m venv .venv
. .venv/Scripts/activate   # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

echo OPENAI_API_KEY=your_key_here > .env
python app.py
```
Backend runs at: `http://localhost:5000`

### 3.2 Key Files

- `app.py` – API routes, evaluator bootstrap, DB init
- `evaluator.py` – GPT‑4o evaluation logic, strict prompt, chunked processing
- `chunking_utils.py` – chunking and combination helpers
- `utils.py` – file save, ZIP extraction with smart filtering
- `models.py` – SQLAlchemy models (`Hackathon`, `Submission`, `Evaluation`)
- `config.py` – configuration (DB, upload limits, model settings)

### 3.3 Configuration (.env)
```
OPENAI_API_KEY=sk-...
```
Other important settings in `config.py`:
- `MAX_CONTENT_LENGTH` – upload limit (default 5GB)
- `ALLOWED_EXTENSIONS` – accepted file types
- SQLite DB path via `SQLALCHEMY_DATABASE_URI`

### 3.4 API Endpoints

- `GET  /` – Health check/info
- `GET  /api/hackathons` – List hackathons
- `POST /api/hackathon` – Create hackathon
- `POST /api/submissions` – Upload and evaluate a project (multipart form)
  - form fields: `hackathon_id`, `team_name`, `participant_email`, `project_name`, `project_description`, `project_files[]`
- `GET  /api/hackathon/<id>/submissions` – List submissions for a hackathon
- `GET  /api/results/<submission_id>` – Single evaluated result
- `GET  /api/debug/submissions` – Debug listing (optional)

### 3.5 Evaluation Flow
1. Files uploaded → saved to `uploads/submission_<id>/`
2. `utils.extract_code_from_files` reads relevant files; ZIPs are unpacked with smart filtering (skip `node_modules`, builds, caches) and size caps.
3. Content is chunked when long; each chunk is evaluated and combined (size‑weighted).
4. Strict prompt enforces objective scoring across 5 metrics plus key-point analyses:
   - Relevance, Technical Complexity, Creativity, Documentation, Productivity
   - Out‑of‑box thinking, Problem‑solving skills, Research capabilities, Business understanding, Use of non‑famous tools
5. Scores + feedback are persisted and returned to the client.

### 3.6 Troubleshooting
- 413 Request Entity Too Large → Increase `MAX_CONTENT_LENGTH` and restart backend
- Blank result page → Check `GET /api/results/:id` response and browser console
- Repeated 7.x scores → strict prompt and low temperature are already enforced; confirm you’re on `gpt‑4o`

---

## 4) Frontend (Svelte 5)

### 4.1 Setup
```bash
cd AutoEval/EvalAI
npm install
npm run dev
```
Frontend runs at: `http://localhost:5173` (proxy to backend for `/api/*`).

### 4.2 Pages & Routing
- `ProjectEvaluator.svelte` – Upload page with drag‑and‑drop, success redirect to `#/result/:id`
- `IndividualResult.svelte` – Detailed result: bars for scores, key‑points section, animated feedback, buttons to upload/leaderboard
- `AllResults.svelte` – Leaderboard sorted by most recent; shows project name, overall score with badge, and evaluation time
- `App.svelte` – Hash router glue

### 4.3 Styling & UX
- Tailwind CSS utilities, animated transitions (`fly`, `scale`, `fade`), accessible buttons and labels
- Mobile‑friendly; bars preferred for clarity and comparison

### 4.4 Build & Deploy
```bash
cd AutoEval/EvalAI
npm run build    # outputs to dist/
```
Serve `dist/` with your preferred static host (Netlify, Vercel, Nginx). Point it to a reachable backend URL.

---

## 5) Data Model (SQLite)

- `Hackathon(id, name, description, evaluation_prompt, criteria, deadline, created_at)`
- `Submission(id, hackathon_id, project_name, team_name, participant_email, project_description, file_paths, code_content, documentation_content, submitted_at, evaluated)`
- `Evaluation(id, submission_id, relevance_score, technical_complexity_score, creativity_score, documentation_score, productivity_score, overall_score, feedback, detailed_scores, evaluated_at)`

---

## 6) Security & Privacy
- Files are stored locally under `uploads/` by submission id.
- API is CORS‑enabled for the local frontend; add auth for multi‑user deployments.
- Do not commit API keys; use `.env`.

---

## 7) Production Checklist
- Set a strong `SECRET_KEY` and real DB URL
- Put Flask behind a reverse proxy (Nginx) and serve via Gunicorn/Uvicorn
- Configure persistent storage for `uploads/` and DB
- Serve the Svelte `dist/` from a CDN or static host

---

## 8) Quick Commands
```bash
# Backend
cd AutoEval && . .venv/Scripts/activate && python app.py

# Frontend
cd AutoEval/EvalAI && npm run dev
```

---

## 9) License
MIT

---

## 10) Support
Open an issue or contact the maintainer.

— Built with Flask, Svelte 5, Tailwind, and OpenAI GPT‑4o.
