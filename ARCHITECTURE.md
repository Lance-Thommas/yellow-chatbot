This document describes the system architecture, data model, API design, streaming approach, authentication flow, and operational considerations.

## High-level overview

The application is split into three main layers:

1. **Frontend (React)** — UI, routing, SSE consumer, and API client.
2. **Backend (FastAPI)** — REST endpoints, SSE streaming endpoint, authentication, DB access, LLM orchestration.
3. **Database (PostgreSQL)** — persistent storage for users, projects (conversations), and messages.

The backend integrates with an external LLM provider (e.g., OpenAI). When a user sends a message, the backend streams LLM tokens back to the frontend using Server-Sent Events (SSE) so the assistant appears to type in real time.

---

## Components

### Frontend

- **Routing:** `react-router` with protected routes to guard authenticated views.
- **API client:** central `api/client.js` that sets `baseURL` and ensures requests include credentials when necessary.
- **SSE Consumer:** `EventSource` connects to `/api/projects/{id}/messages/stream?content=...`. Incoming SSE data are JSON payloads (small token deltas), appended to the assistant message in the UI. The frontend closes SSE on logout, navigation, or errors.
- **State:** Local React state for projects, selected project, messages, typing state, etc. UI is intentionally minimal to emphasize backend functionality.

### Backend (FastAPI)

- **Auth:** JWT tokens are created on login and set as an `HttpOnly` cookie (`access_token`). `get_current_user` middleware/utility decodes the JWT and extracts `sub` (user email).
- **SSE Endpoint:** An async endpoint accepts a user message, sends the prompt to the LLM provider and yields token chunks as SSE messages. The endpoint also writes final messages into the DB (project/messages).
- **DB Access:** SQLAlchemy ORM with `SessionLocal` session generator. `Base.metadata.create_all(bind=engine)` is used for table creation in development; production should use Alembic migrations.
- **LLM integration:** A service layer/function handles calls to the LLM API, including optional chunking/streaming of tokens. The backend receives streamed tokens from the LLM (if supported) and forwards them as SSE events to the client.

---

## Data model (summary)

- **users**
  - `id` (serial/uuid), `email` (unique), `hashed_password`, `created_at`, `updated_at`
- **projects** (conversations)
  - `id` (uuid), `name`, `owner_id` (FK -> users.id), `created_at`, `updated_at`
- **messages**
  - `id` (uuid), `project_id` (FK -> projects.id), `role` (`user`|`assistant`), `content`, `created_at`

---

## Authentication flow

1. Client POSTs credentials to `/api/login/`.
2. Backend verifies password, creates JWT (payload contains `sub=user_email`), returns 200 and sets `access_token` cookie: `HttpOnly; Secure; SameSite=None`.
3. Client uses protected routes. For server CSR/JS calls, include credentials so cookie is sent.
4. `get_current_user` decodes JWT and authorizes requests.
5. `/api/logout/` clears cookie.

**Notes:** Browser cookie partitioning policies and SameSite behavior vary — ensure `Secure; SameSite=None` for cross-site deployments and `credentials: 'include'` on client requests.

---

## Streaming flow (detailed)

1. User types and hits send. Frontend opens an `EventSource` connecting to: GET /api/projects/{id}/messages/stream?content=<encoded message>
2. Backend validates the session (reads JWT cookie), finds project and user.
3. Backend sends prompt to the LLM API (with streaming enabled if available).
4. As the LLM returns token deltas, backend yields SSE messages:
   - SSE default message: `data: {"delta": "<token_text>"}` (partial)
   - On completion: `event: end` then final message chunk `data: {"content": "<final_reply>"}`
5. Frontend appends deltas to the assistant message. When `end` is received, it finalizes the message and optionally triggers name generation for the first message.

---

## API endpoints (summary)

- `POST /api/users/` — Register
- `POST /api/login/` — Login (sets cookie)
- `POST /api/logout/` — Logout (clears cookie)
- `GET /api/check_session/` — Verify session (used by protected route)
- `GET/POST /api/projects/` — List/create conversations
- `GET /api/projects/{projectId}` — Fetch project metadata
- `GET /api/projects/{projectId}/messages` — Fetch messages
- `GET /api/projects/{projectId}/messages/stream?content=...` — SSE streaming for LLM responses
- `POST /api/projects/{projectId}/generate_name` — Helper to create a name for auto-created conversations

---

## Deployment & operational notes

- **Database SSL:** Hosted providers (Neon, Supabase) often require `sslmode=verify-full`. In some host environments you need to provide or point to a root certificate OR use provider-recommended connection flags. Use connection pooling carefully: long SSE connections favour `NullPool` or reducing idle pool times to avoid unexpected connection reuse for streaming tasks.
- **SSE & Workers:** SSE holds a connection open per client. For many concurrent SSE connections, use an async server (Uvicorn with `--loop=asyncio`) and consider fewer worker processes or a separate SSE service. Alternatively use WebSockets or an outboard streaming worker with Redis pub/sub.
- **Scaling LLM calls:** Rate limit LLM calls, use batching or queueing for high concurrency, and cache repeated prompts if appropriate.
- **Logging & monitoring:** Sentry is included. Keep sensitive debug disabled in production.
- **Security:** Strong `SECRET_KEY`, hashed passwords (bcrypt), enforce HTTPS, limit cookie lifetime, CSRF considerations if switching to token-in-header.

---

## Local debug tips

- Use `ngrok` or similar to test webhooks with a public URL.
- When debugging cookies and CORS: ensure backend `CORSMiddleware` has `allow_credentials=True` and frontend calls use `credentials: 'include'`.
- If `check_session` 404s, verify route exists and router prefix `/api` is used consistently.

---

## Further improvements (ideas)

- Add Alembic migrations.
- Swap SSE to WebSocket for bi-directional streaming and improved scale.
- Add Redis-backed job queue for LLM calls and concurrency control.
- Add tests (unit + integration).
