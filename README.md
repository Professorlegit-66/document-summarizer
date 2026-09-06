# Document Summarizer

An AI-powered web application that extracts text from uploaded documents (PDF, DOCX, TXT) and generates a summary using a locally-running large language model via [Ollama](https://ollama.com/). Built as an incremental, milestone-based learning project to practice full-stack development with a real AI integration.

## Features

- Upload PDF, DOCX, or TXT files via click-to-browse or drag-and-drop
- Choose a summary **length** (short / medium / detailed) and **style** (paragraph / bullet points / key takeaways)
- Automatic chunking for long documents, so the AI model's context window isn't exceeded
- Clear, honest loading feedback (elapsed-time counter and rotating status messages) for requests that can take several minutes
- Copy-to-clipboard and download-as-`.txt` for the generated summary
- Light/dark mode, respecting your OS preference on first visit and remembering a manual choice afterward
- Client- and server-side validation with clear, non-technical error messages
- Fully keyboard-operable, with visible focus states and ARIA labeling for screen readers

## Tech Stack

**Backend**
- Python 3.13, FastAPI, Uvicorn
- [PyMuPDF](https://pymupdf.readthedocs.io/) (PDF text extraction) and [python-docx](https://python-docx.readthedocs.io/) (DOCX text extraction)
- [Ollama](https://ollama.com/) running a local open-source model (`llama3.2`, 3B) for summarization, called via `httpx`
- `pydantic-settings` for centralized, environment-variable-driven configuration

**Frontend**
- React + Vite
- Tailwind CSS v4
- Plain JavaScript (no TypeScript)
- [lucide-react](https://lucide.dev/) for icons

## Prerequisites

Before running this project locally, make sure you have:

- **Python 3.13** (or compatible) installed
- **Node.js** (LTS, e.g. 22.x) and npm installed
- **[Ollama](https://ollama.com/download)** installed and running, with the `llama3.2` model pulled:
```bash
  ollama pull llama3.2
```

## Setup & Running Locally

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd document-summarizer
```

### 2. Backend setup

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Copy the example environment file and adjust if needed (the defaults work for a typical local setup):

```powershell
copy .env.example .env
```

Start the backend:

```powershell
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

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

Ollama typically runs as a background service after installation. You can verify it's up by visiting `http://localhost:11434` in a browser, or running:

```bash
ollama list
```

## Usage

1. Open the app in your browser.
2. Upload a PDF, DOCX, or TXT file (up to 10 MB).
3. Choose a summary length and style.
4. Click **Summarize** and wait for the result — small documents typically finish in seconds; longer documents that require chunking can take several minutes, especially on CPU-only hardware.
5. Copy the summary to your clipboard, or download it as a `.txt` file.

## Known Limitations

- **Chunking uses a character-based heuristic** (~4 characters ≈ 1 token) rather than a real tokenizer. This is an approximation — it works well in practice but isn't perfectly precise about how much text actually fits in the model's context window.
- **No overlap between adjacent chunks.** Each chunk is summarized independently; a detail split exactly across a chunk boundary could occasionally be under-represented in the final summary.
- **Fail-fast error handling.** If any single chunk (or the final synthesis step) fails, the entire request fails — there's no partial-result fallback or automatic retry.
- **CPU-only inference** (no dedicated GPU in the reference environment) means multi-chunk documents can take several minutes end-to-end. This is a hardware constraint, not a software bug.
- **No true per-chunk progress reporting.** The frontend shows an elapsed-time counter and rotating status messages rather than real progress (e.g. "chunk 3 of 7"), since that would require polling, Server-Sent Events, or WebSockets — a bigger architectural change deferred to a future milestone.
- **"Key Takeaways" and "Bullet Points" styles can look similar** on documents with little narrative structure (e.g. a flat list of filenames or data), since there isn't much thematic material to differentiate between the two styles on that kind of input. Both styles are clearly distinct on typical prose documents.
- **Theme toggle is a simple Light/Dark switch.** An explicit "follow system" option (in addition to using it only as the first-visit default) is deferred until the app has a dedicated settings area.
- **Not yet deployed.** This project currently runs locally only; a hosted AI API swap, rate limiting, and general production hardening are planned for a future deployment milestone.

## Project Structure

```
document-summarizer/
├── backend/
│   └── app/
│       ├── main.py
│       ├── api/routes/          # FastAPI route handlers
│       ├── services/
│       │   ├── document_parser/ # PDF/DOCX/TXT extraction facade
│       │   ├── text_processing/ # Cleaning, emptiness checks
│       │   └── ai/              # Ollama integration, prompts, chunking
│       ├── models/               # Pydantic request/response models
│       └── core/                 # Configuration
├── frontend/
│   └── src/
│       ├── components/           # UploadArea, SummaryOptions, ResultDisplay, etc.
│       ├── hooks/                # useDarkMode
│       ├── services/              # summarizerService (API client)
│       └── constants/             # Shared options and style constants
└── README.md
```

## License

This project is licensed under the [MIT License](LICENSE).