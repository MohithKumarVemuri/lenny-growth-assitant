# Agent Transcript 01: System Architecture & Scaffolding

**Date:** 2026-09-18  
**Author / Agent:** Antigravity Coding Agent  
**Focus Area:** Foundation Scaffolding, Persistence Layer, and Multi-Provider LLM Abstraction

---

## 1. Initial Challenge & Technical Scope Analysis

When reviewing the assignment requirements for **The Lenny Growth Assistant**, three immediate architectural tensions emerged:
1. **Database Runtime Dependency:** The assignment calls for PostgreSQL with `pgvector` for vector similarity and session persistence. However, an evaluator running on a local machine without Docker running would hit connection errors if we relied solely on an external PostgreSQL instance.
   - *Decision:* Design a hybrid database abstraction in `backend/app/database.py`. In containerized environments (`docker-compose.yml`), it connects to PostgreSQL 16 + `pgvector`. For zero-dependency local runs or CI unit tests, it automatically falls back to an asynchronous SQLite database for relational records and an in-memory normalized cosine similarity index for vectors.
2. **Local Model Availability (Ollama):** The assignment mandates running the demo on local Ollama, but evaluators may have different models installed (`llama3.2:3b`, `llama3.1:8b`, `mistral:7b`) or might need a quick diagnostic if the Ollama daemon isn't started yet.
   - *Decision:* Implement dynamic provider routing with clear status indicators in `GET /api/health`. If Ollama is unreachable, return a structured diagnostic message indicating how to start Ollama (`ollama serve` and `ollama run llama3.2:3b`) with a seamless toggle to cloud providers (Claude 3.5 Sonnet or OpenAI) or a simulation mode.

---

## 2. Directory Hierarchy Decision

We established a clean separation of concerns adhering to enterprise FastAPI patterns:
```
backend/
├── app/
│   ├── api/        # REST & SSE endpoints (sessions, chat, health)
│   ├── models/     # SQLAlchemy ORM and Pydantic schemas
│   ├── providers/  # LLM abstraction (Base, Ollama, Cloud, Factory)
│   ├── rag/        # Embeddings and vector similarity retrieval
│   └── skills/     # Ship 30 for 30 writer & Artifact generator
```

---

## 3. Failed Attempts & Corrections

- **Attempt 1 (Direct Postgres Connection without fallback):**
  Initially attempted a direct `create_async_engine(DATABASE_URL)` expecting Docker to always be running. When testing in local environments where PostgreSQL was inactive, the app crashed at startup.
  - *Correction:* Created `init_db()` with a connection probe. If the Postgres URL fails or `sqlite:///` is specified, it initializes SQLite with SQLAlchemy async SQLite driver and sets a flag for the vector retriever to use normalized numpy/in-memory cosine similarity with pre-indexed transcript chunks.

- **Attempt 2 (SSE Event Formatting for Artifacts):**
  During early streaming design, artifact code chunks were sent as raw strings in the same stream as conversational tokens. This led to UI flickering where markdown code fences broke mid-stream.
  - *Correction:* Structured SSE events with explicit types:
    `{"type": "status", "content": "..."}`  
    `{"type": "sources", "sources": [...]}`  
    `{"type": "token", "content": "..."}`  
    `{"type": "artifact", "artifact": {...}}`  
    `[DONE]`  
  This enables the frontend to route tokens to the chat bubble and artifacts directly to the side canvas.
