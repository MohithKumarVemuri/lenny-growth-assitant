# Architecture Specification
## The Lenny Growth Assistant

---

## 1. System Topology Overview

```
                                  ┌────────────────────────┐
                                  │      Web Browser       │
                                  │   (Next.js / Vite SPA) │
                                  └───────────┬────────────┘
                                              │  HTTPS / SSE
                                              ▼
                                  ┌────────────────────────┐
                                  │    FastAPI Gateway     │
                                  │     (ASGI / Uvicorn)   │
                                  └─────┬────────────┬─────┘
                                        │            │
            ┌───────────────────────────┘            └─────────────────────────┐
            ▼                                                                  ▼
┌───────────────────────┐                                          ┌───────────────────────┐
│     PostgreSQL 16     │                                          │  LLM Provider Layer   │
│  ├── sessions         │                                          │  ├── Ollama (Local)   │
│  ├── messages         │                                          │  ├── Anthropic Claude │
│  ├── artifacts        │                                          │  └── OpenAI GPT-4o    │
│  └── transcript_chunks│                                          └───────────────────────┘
│      (pgvector HNSW)  │
└───────────────────────┘
```

---

## 2. Component Boundaries & Responsibilities

### 2.1 API & Orchestration Layer (FastAPI)
- **ASGI Entrypoint (`app/main.py`):** Configures CORS, structured JSON logging, exception handlers, and registers modular routers.
- **Session Router (`app/api/sessions.py`):** Handles CRUD operations for chat sessions and conversational history.
- **Chat Streaming Router (`app/api/chat.py`):** Accepts conversational queries, computes embedding, executes similarity search, constructs grounded system prompt, dynamically dispatches to active LLM provider, and streams response tokens via Server-Sent Events (SSE).
- **Health Router (`app/api/health.py`):** Probes database connectivity, vector index chunk counts, and model endpoint reachability.

### 2.2 Persistence & Vector Storage (PostgreSQL + pgvector)
- Stores chat conversations, session metadata, generated artifacts, and podcast transcript embeddings.
- Vector distance calculated using Cosine Distance (`<=>`), indexed via `HNSW` (Hierarchical Navigable Small World) for sub-millisecond retrieval.
- **Resilience Fallback:** When PostgreSQL is unavailable (e.g. running in lightweight local test mode), the storage engine automatically initializes a local SQLite database for session persistence and an in-memory normalized vector cosine index for retrieval.

### 2.3 Knowledge Retrieval Layer (RAG Engine)
- **Chunking Pipeline:** Raw podcast markdown transcripts are segmented into semantically coherent chunks ($500\text{--}800$ tokens, $100$-token overlap) with prepended header metadata:
  ```text
  [Episode: {episode_title} | Guest: {guest_name} | Timestamp/Topic: {timestamp_ref}]
  ```
- **Embedding Generation:** High-performance vector embeddings generated via `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional) or compatible embedding provider.
- **Grounding Gate:** Top $K$ ($K=4\text{--}6$) chunks retrieved with similarity threshold filtering ($S \ge 0.60$). If no chunks qualify, retrieval returns empty and the agent triggers an explicit lack-of-grounding response.

### 2.4 LLM Provider Abstraction
All model integrations conform to the unified abstract interface:
```python
class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        pass
```
- **`OllamaProvider`:** Connects asynchronously via `httpx` to `http://localhost:11434/api/chat`.
- **`AnthropicProvider`:** Connects to Anthropic API (`claude-3-5-sonnet-20241022`).
- **`OpenAIProvider`:** Connects to OpenAI API (`gpt-4o`).
- **`ProviderFactory`:** Dynamically resolves provider instance per request based on client preference (`X-Model-Provider` header or request body) with system-level fallback.

---

## 3. Database Schema

```sql
-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 1. Chat Sessions
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL DEFAULT 'New Conversation',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL, -- 'user' | 'assistant' | 'system'
    content TEXT NOT NULL,
    sources JSONB DEFAULT '[]'::jsonb, -- Array of citation objects
    model_provider VARCHAR(50) NOT NULL DEFAULT 'ollama',
    mode VARCHAR(50) NOT NULL DEFAULT 'default', -- 'default' | 'ship30' | 'artifact'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Artifacts
CREATE TABLE artifacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    artifact_type VARCHAR(50) NOT NULL, -- 'html' | 'markdown'
    content TEXT NOT NULL,
    language VARCHAR(50) DEFAULT 'html',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Transcript Chunks & Vectors
CREATE TABLE transcript_chunks (
    id SERIAL PRIMARY KEY,
    episode_title VARCHAR(255) NOT NULL,
    guest_name VARCHAR(255) NOT NULL,
    episode_url VARCHAR(512),
    timestamp_ref VARCHAR(100),
    chunk_text TEXT NOT NULL,
    embedding vector(384) NOT NULL
);

-- HNSW Index for fast vector similarity search
CREATE INDEX IF NOT EXISTS transcript_chunks_embedding_hnsw_idx 
ON transcript_chunks USING hnsw (embedding vector_cosine_ops);
```

---

## 4. API Specification & Request/Response Contracts

### 4.1 Health Probe
`GET /api/health`
- **Response `200 OK`:**
```json
{
  "status": "healthy",
  "database": "connected",
  "vector_count": 142,
  "ollama": {
    "status": "online",
    "model": "llama3.2:3b"
  },
  "cloud_configured": {
    "anthropic": true,
    "openai": false
  }
}
```

### 4.2 Create Session
`POST /api/sessions`
- **Body:**
```json
{
  "title": "PLG Retention Tactics with Elena Verna"
}
```
- **Response `201 Created`:**
```json
{
  "id": "7b5b7b7a-9a99-472e-b6a4-4f48cfb1b11b",
  "title": "PLG Retention Tactics with Elena Verna",
  "created_at": "2026-09-18T15:30:00Z"
}
```

### 4.3 Streaming Chat Endpoint
`POST /api/chat`
- **Body:**
```json
{
  "session_id": "7b5b7b7a-9a99-472e-b6a4-4f48cfb1b11b",
  "message": "What is the difference between founder mode and manager mode according to Brian Chesky?",
  "provider": "ollama",
  "mode": "default"
}
```
- **Streaming Response (`text/event-stream`):**
```text
data: {"type": "status", "content": "Searching transcripts for relevant context..."}

data: {"type": "sources", "sources": [{"episode": "Brian Chesky on Founder Mode", "guest": "Brian Chesky", "timestamp": "14:22", "score": 0.89, "snippet": "..."}]}

data: {"type": "token", "content": "Brian "}
data: {"type": "token", "content": "Chesky explains that "}
...
data: {"type": "artifact", "artifact": {"title": "Founder Mode Checklist", "type": "markdown", "content": "..."}}

data: [DONE]
```

---

## 5. Security Architecture & Artifact Sandboxing

### 5.1 Untrusted Code Isolation Threat Model
Generated HTML/CSS snippets could conceivably contain malicious JavaScript attempting:
1. Cross-Site Scripting (XSS) against the host application.
2. Reading session tokens or sensitive data from `localStorage` or `document.cookie`.
3. Hijacking navigation via `window.top.location`.

### 5.2 Defense-in-Depth Mitigation
1. **DOMPurify Pre-Sanitization:** The raw HTML content is sanitized via DOMPurify before mounting to strip dangerous protocol handlers (`javascript:`, `data:` iframe nesting) while preserving legitimate inline styling, forms, and interactive buttons.
2. **Strict Iframe Sandboxing:** The component renders inside an `<iframe>` configured with:
   ```html
   <iframe
     sandbox="allow-scripts"
     srcdoc={sanitizedHtml}
   />
   ```
   - `allow-scripts`: Permits JavaScript execution for UI interactivity (e.g. calculator sliders, tabs).
   - **Crucially Omits `allow-same-origin`:** Treats the iframe content as a distinct, unique origin (`null`), blocking access to parent DOM, storage, and cookies.
   - **Crucially Omits `allow-top-navigation`:** Prevents the framed code from redirecting the host page.

---

## 6. Observability & Telemetry

- **Structured Logs:** Built using Python `logging` with JSON formatting emitting `timestamp`, `level`, `session_id`, `provider`, `duration_ms`, and `tokens_streamed`.
- **Latency Monitoring:** RAG retrieval duration and model time-to-first-token (TTFT) recorded per turn.
