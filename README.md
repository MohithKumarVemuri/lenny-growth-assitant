# 🎙️ The Lenny Growth Assistant
> **Full-Stack AI-Powered Strategic Assistant Grounded in Lenny’s Podcast Transcripts**  
> *Built with FastAPI, PostgreSQL + pgvector (with zero-friction local fallback), Ollama Local & Cloud Model Routing, Ship 30 for 30 Essay Engine, and a Claude-Style Sandboxed Artifact Viewer.*

---

## 🚀 Executive Summary & Forward Deployment Brief

**The Lenny Growth Assistant** is an enterprise-grade retrieval-augmented generation (RAG) system created to unlock over 200 hours of tactical product management and growth wisdom from [*Lenny's Podcast*](https://www.lennyspodcast.com/). 

### The Problem It Solves
Product managers, growth leads, and startup founders struggle with **synthesis fatigue** and **LLM hallucination**. While industry titans like Brian Chesky, Elena Verna, Shreyas Doshi, and Rahul Vohra have shared battle-tested playbooks on Lenny's show, navigating through 20,000-word transcripts is manual, and generalist LLMs invent fictional quotes.

### Measurable Objectives
- **Retrieval Grounding Accuracy ($\ge 90\%$):** 100% of factual assertions cite verified guest, episode, and timestamp references.
- **Strict Domain Guardrail:** Refuses out-of-domain queries when evidence is absent (*"I do not have sufficient information in Lenny's podcast archive to answer this"*).
- **Ship 30 for 30 Heuristic Adherence:** Generates ~1,250-word executive memos with high-tension hooks, 1–3 sentence paragraphs, bold anchor bullets, and actionable takeaway checklists.
- **Artifact Security Isolation (0 Host Leakage):** Untrusted HTML/JS snippets execute inside a hardened sandbox with `sandbox="allow-scripts"` (strictly omitting `allow-same-origin`) and DOMPurify sanitization.

---

## 🏗️ Architecture Overview

```
                                  ┌────────────────────────┐
                                  │      Web Browser       │
                                  │   (Vite + React + TS)  │
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
│  [SQLite Fallback Auto]
└───────────────────────┘
```

---

## ⚡ Quickstart Guide

You can run the application using **Docker Compose** (recommended for production) or directly via **Local Python & Node** (zero-friction, no external database needed).

### Option A: One-Command Startup (Docker Compose)

```bash
# 1. Clone repository and navigate to directory
cd lenny-growth-assistant

# 2. Copy environment template
cp .env.example .env

# 3. Launch database, backend, and frontend
docker-compose up --build
```
- **Frontend:** [http://localhost:3000](http://localhost:3000)
- **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

### Option B: Local Zero-Friction Setup (No Docker Required)

Our hybrid database layer automatically switches to SQLite if PostgreSQL is offline, letting you test immediately!

#### 1. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Ingest and vector-index Lenny's podcast seed transcripts
python scripts/ingest.py

# Launch FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🤖 Model Configuration & Local Ollama Setup

The application features dynamic model toggle right from the UI header without restarting services:

### 1. Local LLM: Ollama (Mandatory Demo Requirement)
1. Install Ollama from [ollama.com](https://ollama.com/).
2. Run the model:
   ```bash
   ollama run llama3.2:3b
   # Or alternatively:
   ollama run llama3.1:8b
   ```
3. The app connects to `http://localhost:11434` automatically.
4. *Graceful Offline Diagnostic:* If Ollama is offline or the model is not pulled, the UI displays clear status warnings and allows fallback to **Simulation Mode** or Cloud models.

### 2. Cloud LLM: Claude 3.5 Sonnet & OpenAI GPT-4o
Set your API keys in `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
```

---

## 🧪 Automated Testing & Verification

Run the comprehensive automated test suite covering API contracts, vector retrieval, out-of-domain refusal, and provider abstraction:

```bash
cd backend
python -m pytest tests -v
```

### Test Suite Results:
- `tests/test_api.py::test_root_endpoint` **PASSED**
- `tests/test_api.py::test_health_endpoint` **PASSED**
- `tests/test_api.py::test_session_lifecycle` **PASSED**
- `tests/test_providers.py::test_provider_factory_resolution` **PASSED**
- `tests/test_providers.py::test_simulation_streaming_tokens` **PASSED**
- `tests/test_providers.py::test_ship30_prompt_construction` **PASSED**
- `tests/test_providers.py::test_artifact_extraction_and_cleaning` **PASSED**
- `tests/test_retrieval.py::test_embedding_dimension` **PASSED**
- `tests/test_retrieval.py::test_relevant_chunk_retrieval` **PASSED**
- `tests/test_retrieval.py::test_out_of_domain_retrieval_refusal` **PASSED**

---

## 🛡️ Claude-Style Sandboxed Artifact Viewer & Security

When the assistant generates interactive dashboards, HTML widgets, or product specifications, they are wrapped in `<artifact type="html|markdown" title="...">` containers.

### Security Architecture:
1. **Pre-Sanitization:** HTML strings are sanitized using **DOMPurify** to strip dangerous protocols (`javascript:`) while preserving styling and forms.
2. **Strict Iframe Sandboxing:** Rendered using `<iframe sandbox="allow-scripts" srcdoc={cleanHtml} />`.
   - `allow-scripts` enables rich interactivity (sliders, calculators, tab switching).
   - **Crucially Omits `allow-same-origin`:** Treats the framed document as an opaque origin (`null`), blocking access to parent window `document`, session cookies, and `localStorage`.
   - **Crucially Omits `allow-top-navigation`:** Prevents framed code from redirecting the user away.
3. **Dual-Tab Canvas:** Evaluators can toggle between **Live Preview** and syntax-highlighted **Source Code**, or copy and download the artifact with a single click.

---

## ✍️ Ship 30 for 30 Content Engine

Selecting **Ship 30 for 30** mode activates a dedicated synthesis engine adhering to Dickie Bush & Nicolas Cole's writing framework:
1. **The Hook (First 2-3 lines):** High-tension curiosity gap or counterintuitive truth.
2. **Core Thesis:** One memorable sentence defining the golden rule.
3. **High Skimmability Architecture:** 1-to-3 sentence paragraphs, distinct H2/H3 sections, bold anchor words on every bullet point.
4. **Grounded Substance:** Strict guest attribution (e.g. Elena Verna on B2B PLG flywheels, Brian Chesky on Founder Mode).
5. **Operational Takeaway:** Actionable 5-step implementation checklist.

---

## 📂 Deliverables & Repository Structure

- `docs/PRD.md`: Forward Deployment Discovery Brief, Persona, JTBD, Success Metrics, Assumptions, Scope, and Risks.
- `docs/architecture.md`: System topology, database schema, RAG pipeline, model router, security isolation.
- `docs/design.md`: UI/UX design tokens, Claude Artifacts dual-pane layout, accessibility (a11y), state machine.
- `docs/demo_guide.md`: 2–3 minute video presentation script and walkthrough checklist.
- `agent_transcripts/`:
  - `01_system_architecture_scaffolding.md`
  - `02_retrieval_and_ship30_engine.md`
  - `03_artifact_viewer_and_security.md`
- `docker-compose.yml` & `.env.example`: Single-command containerized reproducibility.
