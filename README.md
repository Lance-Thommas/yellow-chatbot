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

### Steps

## 1) Clone

`git clone https://github.com/Lance-Thommas/yellow-chatbot.git
cd yellow-chatbot`

## 2) Backend

`cd backend
python -m venv .venv`

### Activate virtual environment

`source .venv/bin/activate # Windows: .venv\Scripts\activate
pip install -r requirements.txt`

### Set environment variables

`export DATABASE_URL="postgresql://user:pass@host:5432/dbname?sslmode=require"
export SECRET_KEY="replace_with_secure_random"
export OPENAI_API_KEY="sk-..."`

### Run backend

`uvicorn main:app --reload --host 0.0.0.0 --port 8000`

## 3) Frontend

#### Update frontend/api/client.js baseURL to match backend (e.g. http://localhost:8000/api)

`cd ../frontend
npm install
npm run dev`

## 4) Minimal API overview

### POST /api/login/ — login (sets access_token cookie)

### POST /api/logout/ — logout (clears cookie)

### GET /api/check_session/ — quick session check

### GET /api/projects/ — list conversations

### POST /api/projects/ — create conversation

### GET /api/projects/{id}/messages/ — fetch messages

### GET /api/projects/{id}/messages/stream?content=... — SSE streaming of LLM response
