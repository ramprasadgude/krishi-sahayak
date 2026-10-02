# 🌾 Krishi Sahayak

A voice-first AI advisory assistant for farmers — ask a question in Telugu, get a
grounded, spoken-back answer. No typing, no English, no hunting across portals.

Built for **Build Fast with AI: AI Build Challenge 2026** (Unstop) —
Problem Statement 6: *AI for Bharat (Indian Languages)*.

## How it works

```
Voice input (Telugu) → Speech-to-Text (Whisper) → Translate to English
    → Retrieve (TF-IDF over curated knowledge base) → Answer generation (Claude)
    → Translate to Telugu → Text-to-Speech (gTTS) → Spoken answer
```

Every answer is grounded in a curated knowledge base (`backend/app/data/knowledge_base.json`)
covering crop advisory (paddy, cotton, chilli, groundnut, tomato) and government
schemes (PM-KISAN, PMFBY crop insurance). If a question falls outside that
knowledge base, the assistant says so instead of guessing.

## Project structure

```
krishi-sahayak/
├── backend/           FastAPI app — the voice pipeline
│   ├── app/
│   │   ├── main.py            API routes
│   │   ├── models.py          request/response schemas
│   │   ├── data/               knowledge_base.json
│   │   └── services/
│   │       ├── stt.py          speech-to-text (OpenAI Whisper)
│   │       ├── translate.py    Telugu <-> English (Google Translate)
│   │       ├── retrieve.py     RAG retrieval (TF-IDF)
│   │       ├── answer.py       grounded answer generation (Claude)
│   │       └── tts.py          text-to-speech (gTTS)
│   ├── requirements.txt
│   ├── .env.example
│   └── render.yaml             Render deployment blueprint
└── frontend/          React (Vite) app — voice/text chat UI
    ├── src/
    │   ├── App.jsx
    │   ├── api.js
    │   └── components/
    │       ├── VoiceRecorder.jsx
    │       └── ChatBubble.jsx
    ├── package.json
    └── vercel.json             Vercel deployment config
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- An [OpenAI API key](https://platform.openai.com/api-keys) (speech-to-text)
- An [Anthropic API key](https://console.anthropic.com/) (answer generation)

Both translation (deep-translator) and text-to-speech (gTTS) are free and need
no API key.

## 1. Local setup — backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and fill in OPENAI_API_KEY and ANTHROPIC_API_KEY

uvicorn app.main:app --reload --port 8000
```

Check it's running: open http://localhost:8000/api/health — you should see
`{"status": "ok", "knowledge_base_size": 13}`.

Interactive API docs are auto-generated at http://localhost:8000/docs, where
you can try `/api/text-query` directly without the frontend.

## 2. Local setup — frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (usually http://localhost:5173). The dev server
proxies `/api/*` calls to the backend on port 8000 automatically (see
`vite.config.js`), so no extra config is needed for local development.

Tap the mic and speak a question in Telugu, or use the text box — try one of
the sample questions shown on first load.

## 3. Deploying the backend (Render)

1. Push this repo to GitHub (see step 5 below).
2. Go to [Render](https://render.com) → **New +** → **Blueprint**, and point
   it at your GitHub repo. Render will read `backend/render.yaml` automatically.
   (Alternatively: **New +** → **Web Service**, set root directory to
   `backend`, build command `pip install -r requirements.txt`, start command
   `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.)
3. In the service's **Environment** tab, add:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `ALLOWED_ORIGINS` — set this once you have your Vercel URL (step 4), e.g.
     `https://krishi-sahayak.vercel.app`
4. Deploy. Note the public URL Render gives you, e.g.
   `https://krishi-sahayak-backend.onrender.com`.

## 4. Deploying the frontend (Vercel)

1. Go to [Vercel](https://vercel.com) → **Add New** → **Project**, import the
   same GitHub repo, and set the **root directory** to `frontend`.
2. Add an environment variable:
   - `VITE_API_BASE_URL` = your Render backend URL from step 3
     (e.g. `https://krishi-sahayak-backend.onrender.com`)
3. Deploy. Vercel will give you a public URL, e.g.
   `https://krishi-sahayak.vercel.app`.
4. Go back to Render and set `ALLOWED_ORIGINS` to that Vercel URL, then
   redeploy the backend so CORS allows requests from your live frontend.

Your deployed link for the challenge submission is the Vercel URL.

## 5. Pushing to GitHub

```bash
cd krishi-sahayak
git init
git add .
git commit -m "Initial commit: Krishi Sahayak MVP"
git branch -M main
git remote add origin https://github.com/<your-username>/krishi-sahayak.git
git push -u origin main
```

`.env` is already excluded via `.gitignore` — double-check it wasn't staged
(`git status`) before your first push so no API keys leak into the repo.

## AI tools disclosure

| Tool | Used for |
|---|---|
| Claude (Anthropic) | Code scaffolding, grounded answer generation at runtime, and this project's pitch deck |
| OpenAI Whisper API | Speech-to-text for Telugu voice input |
| Google Translate (via deep-translator) | Telugu ↔ English translation (MVP choice; see note below) |
| gTTS | Text-to-speech for the spoken Telugu answer (MVP choice; see note below) |

**Note on translation/TTS:** the pitch deck's target production stack is
AI4Bharat IndicTrans2 / Bhashini, which are tuned specifically for Indian
languages. For this challenge build, Google Translate and gTTS were used
instead since they need no API registration and kept the MVP shippable
within the timeline — `translate.py` and `tts.py` are isolated modules
specifically so that swap is a small, contained change later.

## Known MVP limitations

- Knowledge base covers 5 crops and 2 schemes — intentionally scoped for a
  demoable MVP, not production coverage.
- Google Translate and gTTS depend on outbound internet access from the
  backend; they are unofficial free wrappers, not SLA-backed services —
  fine for a demo, not for production load.
- No persistent conversation memory between questions (each query is
  independent) — this is a possible Phase 2 addition.
