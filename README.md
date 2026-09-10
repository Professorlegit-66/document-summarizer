# Document Summarizer

An AI-powered web application that extracts text from uploaded documents (PDF, DOCX, TXT) and generates a summary using a large language model. Supports two AI backends: a locally-running open-source model via [Ollama](https://ollama.com/) for development, and [Groq](https://groq.com/)'s hosted API for production. Built as an incremental, milestone-based learning project to practice full-stack development with a real AI integration, including deployment.

## Live Demo

**[https://document-summarizer.talhakhan111221.workers.dev](https://document-summarizer.talhakhan111221.workers.dev)**

Hosted on free tiers throughout (Cloudflare Workers for the frontend, Render for the backend, Groq's free API tier for AI inference) — see [Known Limitations](#known-limitations) for what that means in practice (cold starts, shared rate limits).

## Features

- Upload PDF, DOCX, or TXT files via click-to-browse or drag-and-drop
- Choose a summary **length** (short / medium / detailed) and **style** (paragraph / bullet points / key takeaways)
- Automatic chunking for long documents, so the AI model's context window isn't exceeded
- Clear, honest loading feedback (elapsed-time counter and rotating status messages) for requests that can take over a minute
- Copy-to-clipboard and download-as-`.txt` for the generated summary
- Light/dark mode, respecting your OS preference on first visit and remembering a manual choice afterward
- Client- and server-side validation with clear, non-technical error messages
- Fully keyboard-operable, with visible focus states and ARIA labeling for screen readers
- Per-IP rate limiting to protect shared AI usage quotas in production

## Tech Stack

**Backend**
- Python 3.13, FastAPI, Uvicorn
- [PyMuPDF](https://pymupdf.readthedocs.io/) (PDF text extraction) and [python-docx](https://python-docx.readthedocs.io/) (DOCX text extraction)
- AI: [Ollama](https://ollama.com/) (local dev, `llama3.2` 3B) or [Groq](https://groq.com/) (production, `openai/gpt-oss-20b`), selected via an `AI_PROVIDER` setting, both called via `httpx` through a shared abstraction
- [`slowapi`](https://github.com/laurentS/slowapi) for IP-based rate limiting
- `pydantic-settings` for centralized, environment-variable-driven configuration

**Frontend**
- React + Vite
- Tailwind CSS v4
- Plain JavaScript (no TypeScript)
- [lucide-react](https://lucide.dev/) for icons

**Deployment**
- Backend: [Render](https://render.com/) (free Web Service tier)
- Frontend: [Cloudflare Workers](https://workers.cloudflare.com/) (static assets, free tier)

## Prerequisites (Local Development)

- **Python 3.13** (or compatible)
- **Node.js** (LTS, e.g. 22.x) and npm
- **[Ollama](https://ollama.com/download)** installed and running locally, with the `llama3.2` model pulled:
```bash
  ollama pull llama3.2
```
  (Only needed for local development — the live demo uses Groq in production, and you don't need Ollama just to use the deployed app.)

## Setup & Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/Professorlegit-66/document-summarizer.git
cd document-summarizer
```

### 2. Backend setup

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`. The default `.env` values run entirely against local Ollama — no Groq account needed for local dev.

### 3. Frontend setup

In a separate terminal:

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

The app will be available at `http://localhost:5173`.

### 4. Make sure Ollama is running

```bash
ollama list
```

## Usage

1. Open the app (locally or via the [live demo](#live-demo)).
2. Upload a PDF, DOCX, or TXT file (up to 10 MB).
3. Choose a summary length and style.
4. Click **Summarize** and wait for the result — small documents typically finish in seconds; longer documents that require chunking take longer (roughly 2+ minutes in production, due to deliberate rate-limit pacing — see below).
5. Copy the summary to your clipboard, or download it as a `.txt` file.

## Known Limitations

**Core summarization logic:**
- **Chunking uses a character-based heuristic** (~4 characters ≈ 1 token) rather than a real tokenizer.
- **No overlap between adjacent chunks.** A detail split exactly across a chunk boundary could occasionally be under-represented in the final summary.
- **Fail-fast error handling.** If any single chunk (or the final synthesis step) fails, the entire request fails — no partial-result fallback or automatic retry.
- **No true per-chunk progress reporting.** The frontend shows an elapsed-time counter and rotating status messages rather than real progress, since real progress would require polling, SSE, or WebSockets — deferred as a bigger architectural change.
- **"Key Takeaways" and "Bullet Points" styles can look similar** on documents with little narrative structure (e.g. a flat list of filenames), since there isn't much thematic material to differentiate on that kind of input.
- **Theme toggle is a simple Light/Dark switch**, without an explicit "follow system" option beyond the first-visit default.

**Production deployment specifics:**
- **Cold starts.** Render's free tier spins down the backend after ~15 minutes of inactivity; the next request can take 50+ seconds before the app responds, on top of normal processing time.
- **Groq's free-tier rate limits are shared across all users, not per-visitor.** The account-wide budget is 30 requests/minute, 8,000 tokens/minute, 1,000 requests/day, 200,000 tokens/day. A single long, chunked document can use 15,000–20,000 tokens by itself. Long documents are deliberately paced (a 30-second delay between AI calls) to stay under the per-minute ceiling — this is why long documents take noticeably longer in production (~2+ minutes) than they would running locally against Ollama on a fast machine, or than Groq's raw inference speed alone would suggest.
- **Per-IP rate limiting (5 requests/hour, 15/day) protects against any single visitor** exhausting the shared Groq quota, but does **not** prevent multiple different visitors from collectively exhausting it around the same time — at that traffic level, requests could fail with a "usage limit reached" message even though no individual visitor exceeded their own limit.
- **Rate-limit counters are stored in memory, not a persistent store (e.g. Redis).** They reset whenever the backend process restarts — which happens on every redeploy, and also happens automatically whenever the free-tier instance spins down from inactivity and later wakes back up. In practice, this means the rate limit's protection is weaker than it would be with persistent storage, since a restart (including one caused just by normal free-tier idling) clears everyone's counters. Adding Redis-backed storage would fix this, but was judged out of scope for this project's low-traffic, personal/demo purpose.
- **Not designed for concurrent heavy use.** This app was built and deployed for low-traffic, personal/demo purposes, not to handle many simultaneous users.

## Project Structure

```
document-summarizer
│
├── backend
│ └── app
│ ├── main.py
│ ├── api/routes              # FastAPI route handlers
│ ├── services
│ │ ├── document_parser       # PDF/DOCX/TXT extraction facade
│ │ ├── text_processing       # Cleaning, emptiness checks
│ │ └── ai                    # Ollama/Groq integration, prompts, chunking
│ ├── models                  # Pydantic request/response models
│ └── core                    # Configuration, rate limiter
│
├── frontend
│ ├── wrangler.jsonc          # Cloudflare Workers deployment config
│ └── src
│ ├── components              # UploadArea, SummaryOptions, ResultDisplay, etc.
│ ├── hooks                   # useDarkMode
│ ├── services                # summarizerService (API client)
│ └── constants               # Shared options and style constants
│
└── README.md
```

## License

This project is licensed under the [MIT License](LICENSE).
