A conversational AI platform (chatbot) built with **FastAPI**, **PostgreSQL**, and **React**. Focused on backend engineering and LLM integration: persistent conversations, streaming AI responses, and secure session handling.

**Live demo:** https://yellow-chatbot.vercel.app/
**Source:** https://github.com/Lance-Thommas/yellow-chatbot

---

## Key features

- LLM integration for assistant responses (token/streaming support)
- Real-time streaming of AI responses (SSE) for natural “typing” effect
- Secure authentication (JWT in HttpOnly cookie) and protected routes
- Persistent conversations stored as “projects” with messages
- Minimal frontend UX implemented in React for quick iteration

---

## Tech stack

- Frontend: React, react-router, Fetch / Axios
- Backend: FastAPI, Uvicorn, SQLAlchemy
- Database: PostgreSQL (Neon)
- LLM: OpenAI
- Deployment: Render / Vercel

---

## Quickstart (run locally)

### Prereqs

- Node.js (>=18)
- Python (>=3.10)
- PostgreSQL or a hosted Postgres (Neon, Supabase, etc.)

### 1) Clone

bash
git clone https://github.com/Lance-Thommas/yellow-chatbot.git
cd your-repo

### 2) Backend

cd backend
python -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\activate
pip install -r requirements.txt

### create a .env or set env vars:

#### DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, OPENAI_API_KEY

export DATABASE_URL="postgresql://user:pass@host:5432/dbname?sslmode=require"
export SECRET_KEY="replace_with_secure_random"
export OPENAI_API_KEY="sk-..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000

### 3) Frontend

cd frontend
npm install

# update frontend/api/client.js baseURL to match backend (e.g. http://localhost:8000/api)

npm run dev

Minimal API overview

POST /api/users/ — register user

POST /api/login/ — login (sets access_token cookie)

POST /api/logout/ — logout (clears cookie)

GET /api/check_session/ — quick session check

GET /api/projects/ — list conversations

POST /api/projects/ — create conversation

GET /api/projects/{id}/messages/ — fetch messages

GET /api/projects/{id}/messages/stream?content=... — SSE streaming of LLM response
