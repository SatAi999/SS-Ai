# SehatSakhi AI

A voice-first AI healthcare assistant for ASHA workers and rural healthcare workers in India.

Built with **React 18 + Vite** (frontend) and **FastAPI** (backend).

---

## Features

- **Voice-first interaction** — speak in Hindi or English
- **AI-powered health guidance** — symptom analysis, vitals interpretation, emergency triage
- **Medical image analysis** — MedGemma (local) or GPT-4o Vision (cloud)
- **Multilingual** — English and Hindi (हिंदी)
- **Safety-first** — safety guardrail agent prevents unsafe medical advice
- **Offline-capable LLM** — Ollama support for fully local inference

---

## Project Structure

```
SS-Ai/
├── frontend/          React + Vite + TailwindCSS
└── backend/           FastAPI + SQLAlchemy + async Python
```

---

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- (Optional) CUDA GPU for MedGemma local inference
- (Optional) Ollama for local LLM

### 1. Clone & configure

```bash
git clone <repo>
cd SS-Ai
cp .env.example backend/.env
```

Edit `backend/.env` with your API keys.

### 2. Backend setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

**Ingest sample knowledge base (optional):**

```bash
python -m rag.ingestion
```

**Start the backend:**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

---

## Environment Variables

See `.env.example` for all configuration options.

### Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `openai` | `openai`, `groq`, or `ollama` |
| `STT_PROVIDER` | `whisper_api` | `whisper_api` or `faster_whisper` |
| `TTS_PROVIDER` | `edge_tts` | `edge_tts` or `elevenlabs` |
| `VISION_PROVIDER` | `openai_vision` | `openai_vision` or `medgemma` |
| `DATABASE_URL` | SQLite | SQLite (dev) or PostgreSQL (prod) |

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/chat/message` | Send text message |
| `POST` | `/api/voice/transcribe` | Transcribe audio (STT) |
| `POST` | `/api/voice/synthesize` | Text-to-speech |
| `POST` | `/api/vision/analyze` | Analyze medical image |
| `POST` | `/api/sessions/create` | Create new session |
| `GET` | `/api/sessions/{id}` | Get session with messages |
| `GET` | `/api/sessions/history` | Paginated session history |

---

## Safety & Ethics

SehatSakhi AI is designed to **support** healthcare workers, not replace qualified medical professionals.

- Never provides definitive diagnoses
- Never recommends specific medications
- Always encourages consulting a doctor
- Safety guardrail agent reviews all responses
- Emergency escalation to 108 (India ambulance) for critical situations

---

## Tech Stack

**Frontend**: React 18, Vite 5, TailwindCSS 3.4, Framer Motion, Zustand, React Query

**Backend**: FastAPI, SQLAlchemy 2.0 (async), Pydantic v2, aiosqlite

**AI**: OpenAI GPT-4o, Groq Llama3-70B, Ollama, MedGemma 4B (4-bit quantized)

**Voice**: OpenAI Whisper (STT), ElevenLabs / edge-tts (TTS)

**RAG**: ChromaDB

---

## License

MIT
