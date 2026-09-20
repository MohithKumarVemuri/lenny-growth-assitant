# Video Demo Guide & Evaluator Script
## The Lenny Growth Assistant (2–3 Minutes Walkthrough)

---

## 1. Overview & Setup Checklist

Before recording your video demo (with camera enabled on Loom or OBS), make sure:
- [ ] Backend is running on port `8000` (or Docker container is healthy).
- [ ] Frontend is running on port `5173` or `3000`.
- [ ] Seed transcripts are indexed (`python backend/scripts/ingest.py`).
- [ ] Browser window has the app open with clear view of both the Chat Pane and Artifact Viewer.
- [ ] Ollama is running (`ollama run llama3.2:3b` or `llama3.1:8b`) or running in simulated/cloud toggle mode.

---

## 2. Timed Script & Walkthrough (Target: 2 min 45 sec)

### Segment 1: The Problem & Introduction (0:00 – 0:35)
- **Visual:** Camera on speaker, app home screen visible in background.
- **Talking Points:**
  > *"Hi everyone, I'm presenting **The Lenny Growth Assistant**—an AI-powered forward-deployment solution that unlocks operational product management and growth wisdom from over 200 hours of Lenny’s Podcast transcripts."*
  > *"The core problem we solved is synthesis fatigue and hallucination. Product managers and founders often know that leaders like Brian Chesky, Elena Verna, or Shreyas Doshi shared specific playbooks on Lenny's show, but searching through 20,000-word transcripts is painful, and standard LLMs hallucinate non-existent quotes."*
  > *"Our system provides 100% source-grounded answers with interactive citations, a dedicated Ship 30 for 30 essay engine, and a Claude-style sandboxed artifact viewer for live interactive tools."*

### Segment 2: Architecture & Local Ollama Demonstration (0:35 – 1:20)
- **Visual:** Switch screen to app header, point to Model Selector showing **Ollama (Local)**.
- **Talking Points:**
  > *"First, let's look at the model configuration. Notice here in the top bar: we are currently running on **Ollama with a local 3B model**, operating entirely offline on this machine."*
  > *"Let's ask a complex product question: 'What is founder mode according to Brian Chesky, and how does it contrast with manager mode?'"*
  > *(Hit enter, observe streaming response and citations populating).*
  > *"Notice how the answer streams in real-time. Above the response, we get explicit source citations linking directly to the episode: 'Brian Chesky on Founder Mode'. Clicking any citation displays the exact verbatim transcript excerpt retrieved via pgvector."*

### Segment 3: The Ship 30 for 30 Engine (1:20 – 1:55)
- **Visual:** Select **Ship 30 for 30** mode from the UI pills or mode selector.
- **Talking Points:**
  > *"Now, let's switch to the **Ship 30 for 30 Content Skill**. Instead of a generic prompt, we built a dedicated synthesis engine that turns grounded insights into a 1,250-word high-retention essay."*
  > *"Let's prompt: 'Generate an executive essay on Elena Verna's B2B Product-Led Growth flywheel and Product-Led Sales.'*"
  > *"Look at the structure: a compelling curiosity hook in the first three lines, short 1-to-3 sentence paragraphs, bold anchor words on bullet points, and an actionable tactical conclusion, all strictly attributed to Elena Verna's transcript."*

### Segment 4: Claude-Style Sandboxed Artifact Viewer & Security (1:55 – 2:30)
- **Visual:** Ask for an artifact: *"Create an interactive retention calculator widget with sliders for Day 1, Day 7, Day 30 retention."*
- **Talking Points:**
  > *"Next is our Claude-style **Artifact Viewer**. When the user requests a code prototype, spec, or dashboard, the assistant generates an isolated artifact that immediately slides open in the right-hand canvas."*
  > *"Let's look at the live preview: this is a fully functional interactive HTML/CSS/JS retention calculator. But critically, from a security standpoint: generated HTML is untrusted. We isolate this preview inside a sandboxed iframe with `sandbox='allow-scripts'` and strictly omit `allow-same-origin`. We also pre-sanitize markup through DOMPurify. This completely prevents malicious scripts from touching parent cookies, localStorage, or hijacking page navigation."*
  > *"Users can switch to the 'Code' tab, inspect the clean markup, or copy and download it with one click."*

### Segment 5: Technical Trade-off & Closing (2:30 – 2:50)
- **Visual:** Bring camera full or split with architecture diagram.
- **Talking Points:**
  > *"One key technical trade-off we navigated was between local 3B/8B model inference limits and cloud models. Smaller local models can struggle with 1,250-word structural consistency if given massive context. We solved this with focused semantic chunking (500–800 tokens with HNSW pgvector indexing) and prompt contracts that enforce the Ship 30 structure without blowing past the context window."*
  > *"The entire system is containerized with Docker Compose, features automated tests for retrieval and routing, and can be switched dynamically between Ollama, Claude 3.5 Sonnet, and GPT-4o. Thank you!"*
