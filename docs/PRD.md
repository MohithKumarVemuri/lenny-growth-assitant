# Product Requirements Document (PRD)
## The Lenny Growth Assistant

---

## 1. Forward Deployment Discovery Brief

### 1.1 Executive Summary
**The Lenny Growth Assistant** is an enterprise-grade, retrieval-augmented intelligence system designed to unlock operational knowledge from *Lenny’s Podcast* and newsletter transcripts. Built for Product Managers, Growth Leads, Founders, and Strategy Operators, the application eliminates hundreds of hours of manual audio scrubbing by delivering source-grounded answers, generating formatted long-form executive essays under the **Ship 30 for 30** framework, and rendering interactive product artifacts in a secure, sandboxed Claude-style viewer.

### 1.2 User Persona and Problem Statement
- **Primary Persona:** Growth Product Manager & Strategy Leader (*"Growth Lead Alex"*).
  - *Context:* Alex needs to design a retention loop, draft an ICP qualification scorecard, or establish product-market fit metrics before a quarterly executive review.
  - *The Job-to-be-Done (JTBD):* When formulating product strategy or operating plans, Alex wants instant access to the exact heuristics, frameworks, and metrics shared by world-class leaders (e.g., Brian Chesky, Elena Verna, Shreyas Doshi, Rahul Vohra) so they can make defensible decisions without wasting 200+ hours listening to audio or reading fragmented notes.
  - *Pain Removed:* 
    1. Removes subjective guesswork by grounding every recommendation in battle-tested operator playbooks.
    2. Removes synthesis fatigue by auto-generating complete, skimmable 1,250-word strategic memos formatted according to Ship 30 for 30 principles.
    3. Removes context switching by rendering interactive tools (scorecards, calculators, specs) natively inside the app beside the chat.

### 1.3 Measurable Success Metrics
1. **Retrieval Grounding Precision ($\ge 90\%$):** 9 out of 10 factual claims in default mode must map directly to an episode title, guest, and timestamp. Zero hallucinated guest attributions.
2. **Strict Guardrail Compliance ($100\%$):** Queries outside Lenny's podcast domain (e.g., cooking recipes, general trivia) must trigger an explicit refusal: *"I do not have sufficient information in Lenny's podcast archive to answer this."*
3. **Local Inference Latency ($< 4\text{s}$ Time-to-First-Token):** Local Ollama runtime achieves responsive streaming for live demonstrations on standard workstation hardware.
4. **Content Quality (Ship 30 for 30 Score $\ge 95\%$):** Generated essays must hit $\approx 1,250$ words, feature a high-curiosity hook, short paragraphs (1–3 sentences), bold anchor tags on bullets, and an actionable takeaway framework.
5. **Security Isolation ($0$ Parent Leakage):** Untrusted HTML artifacts must be prevented from accessing `window.parent`, localStorage, session cookies, or triggering cross-site scripting (XSS).

### 1.4 Important Assumptions
1. **Transcript Source:** Ingested data originates from the curated markdown archives in [ChatPRD/lennys-podcast-transcripts](https://github.com/ChatPRD/lennys-podcast-transcripts). Transcripts are pre-cleaned and segmented into identifiable episodes with guest names and timestamps.
2. **Hardware Constraints:** Evaluators may run the application on varied hardware ranging from Apple Silicon to multi-core Windows/Linux laptops. The local model tier must default to efficient small language models (`llama3.2:3b` or `mistral:7b`), with graceful fallback simulation if the Ollama daemon is temporarily offline.
3. **Storage Resilience:** PostgreSQL with the `pgvector` extension provides vector and relational storage in containerized deployment. For zero-dependency local evaluation, an automatic fallback to local SQLite + vectorized cosine indexing ensures tests and UI function immediately.

### 1.5 Scope Choices & Explicit Non-Goals
- **In Scope:**
  - High-precision semantic chunking (500–800 tokens with 100-token overlap) preserving episode and guest metadata.
  - RAG conversational pipeline with citation cards and similarity threshold gating.
  - Dedicated Ship 30 for 30 content generation skill.
  - Interactive dual-pane Claude-style Artifact Viewer with live HTML/CSS sandbox rendering and Markdown view.
  - Dynamic model toggle (Ollama Local vs. Anthropic Claude vs. OpenAI GPT-4o) switchable in real-time from the UI header.
  - Session history persistence, deletion, and context recovery.
  - Complete Docker Compose setup, structured JSON logging, and automated test suite.
- **Intentionally Excluded:**
  - *Live Podcast Audio Transcription:* Assumed transcripts are already text.
  - *Multi-tenant user authentication (OAuth/SSO):* Unnecessary overhead for the evaluator; focused on robust session-based multi-turn persistence.
  - *Full web search fallback:* Excluded to enforce strict grounding in Lenny's transcript archive.

### 1.6 Key Risks & Mitigation Trade-offs
| Risk | Severity | Mitigation Strategy |
| :--- | :--- | :--- |
| **Local Model Hallucination & Citation Drift** | High | System prompt strictly penalizes ungrounded claims. Chunks are prepended with verified episode metadata headers. If top similarity score is below $0.65$, refusal is enforced. |
| **Untrusted HTML/XSS in Artifacts** | Critical | Artifact iframe uses `sandbox="allow-scripts"` while strictly omitting `allow-same-origin`. Markup is sanitized through DOMPurify prior to injection. |
| **Ollama Service Downtime during Demo** | Medium | The client and backend employ an automatic health probe. If Ollama is unreachable, the system surfaces clear diagnostic guidance in the UI and allows one-click switching to cloud or simulated mode. |
| **Long Context Window Degradation** | Medium | Chunks are retrieved with top-$K$ relevance ($K=4\text{--}6$) rather than stuffing entire 20,000-word transcripts, keeping prompts within 4,000 tokens for optimal local model performance. |

---

## 2. Product Functional Requirements

### 2.1 Session & Conversation Management
- **FR-1.1:** The user can create new conversation sessions at any time.
- **FR-1.2:** Each session must maintain isolated conversation history and retrieved citations.
- **FR-1.3:** Sessions can be renamed, listed, switched, and deleted from the navigation sidebar.
- **FR-1.4:** Returning to an earlier session restores past messages, citations, and generated artifacts.

### 2.2 Model Selection & Dynamic Routing
- **FR-2.1:** A visible Model Selector badge in the UI header displays active runtime (`Ollama (Local)`, `Claude 3.5 Sonnet`, or `GPT-4o`).
- **FR-2.2:** Switching models takes effect immediately on the next prompt without restarting the application.
- **FR-2.3:** API requests transmit the target provider via payload or request header, allowing fine-grained testing.

### 2.3 Grounded Knowledge Retrieval & Citations
- **FR-3.1:** Incoming queries are vectorized and compared against transcript chunks in PostgreSQL `pgvector`.
- **FR-3.2:** Every answer in Default Mode must render citation badges referencing the Episode Title, Guest Name, and Topic/Timestamp.
- **FR-3.3:** Clicking a citation card exposes the verbatim transcript excerpt retrieved by the system.
- **FR-3.4:** If no retrieved chunk matches the query with sufficient cosine similarity, the model refuses to answer.

### 2.4 Ship 30 for 30 Content Engine
- **FR-4.1:** Users can trigger Ship 30 for 30 mode via the mode toggle or by requesting an essay.
- **FR-4.2:** Generates an essay of approximately 1,250 words structured with:
  1. High-tension Curiosity Hook (lines 1–3).
  2. The Golden Rule / Core Premise.
  3. 3–5 Modular Actionable Sections with bold anchor bullets.
  4. Operational Playbook / Implementation Checklist.
  5. Grounded guest attribution throughout.

### 2.5 Sandboxed Artifact Generation & In-App Viewer
- **FR-5.1:** When the prompt asks for an interactive tool, component, checklist, or document, the assistant wraps it inside an `<artifact type="html|markdown" title="...">` container.
- **FR-5.2:** The frontend detects artifact tags and slides open a Claude-style dual pane viewer on the right.
- **FR-5.3:** For HTML artifacts, the viewer provides a "Preview" tab (sandboxed iframe) and a "Code" tab (syntax-highlighted raw source).
- **FR-5.4:** Users can copy source code or download the artifact as a standalone file (`.html` or `.md`).

---

## 3. Non-Functional Requirements
- **NFR-1 (Portability):** System runs via `docker-compose up --build` or manual run scripts across Windows, macOS, and Linux.
- **NFR-2 (Observability):** Structured logging across API routes, retrieval latency, and model token usage.
- **NFR-3 (Accessibility):** Full keyboard navigation, semantic HTML, high-contrast typography, and ARIA labels.
- **NFR-4 (Security):** Zero hardcoded API keys; safe `.env.example` templates; strict Content-Security-Policy principles for iframes.
