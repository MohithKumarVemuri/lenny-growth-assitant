# Agent Transcript 02: Retrieval-Augmented Generation & Ship 30 for 30 Skill

**Date:** 2026-09-18  
**Author / Agent:** Antigravity Coding Agent  
**Focus Area:** Transcript Chunking, Semantic Grounding, Cosine Thresholding, and Ship 30 Heuristics

---

## 1. Grounding Strategy & Chunking Experiments

When processing transcripts from *Lenny’s Podcast*, naive fixed-size chunking (e.g. every 500 characters) broke conversational question-answer pairs between Lenny and the guest, stripping crucial context.

### Optimal Chunking Heuristic:
- **Chunk Size:** 500 to 800 tokens (approx. 2,000–3,200 characters) with a 100-token sliding overlap.
- **Metadata Prepending:** Every chunk is prepended with explicit header context:
  `[Episode: {episode_title} | Guest: {guest_name} | Section: {topic}]`
- **Result:** Even if a local LLM only receives 4 chunks, it always has unambiguous knowledge of who is speaking and which episode it came from.

---

## 2. Guardrails & Refusal Tuning

To satisfy the strict requirement that answers are grounded exclusively in Lenny’s transcripts:
- We calculated cosine similarity scores between the query embedding and stored chunk vectors.
- **Threshold Tuning:**
  - When similarity $\ge 0.60$, retrieved chunks are injected into the prompt context with citation keys `[Source 1]`, `[Source 2]`.
  - When maximum similarity $< 0.60$ (e.g., questions like *"How do I change a car tire?"* or *"What is the capital of Peru?"*), the retriever returns an empty chunk list.
  - The system prompt instructs:
    *"If the provided context does not contain the answer, reply strictly: 'I do not have sufficient information in Lenny's podcast archive to answer this.'"*

---

## 3. The Ship 30 for 30 Essay Framework Formulation

Rather than a simple "write a long essay" prompt, we encoded the exact writing principles of Dickie Bush & Nicolas Cole’s *Ship 30 for 30*:
1. **The Hook (First 2–3 sentences):** An arresting counterintuitive statement or high-stakes tension.
2. **The Golden Rule / 1-Sentence Insight:** The core thesis boiled down to a memorable takeaway.
3. **High Skimmability Architecture:**
   - Paragraph limit: 1 to 3 sentences maximum. No walls of text.
   - Headers: Clear H2 and H3 anchors.
   - Bold Anchor Tags: Every bullet must start with 2–4 bolded words indicating the core concept.
4. **Substance Grounding:** Specific quotes, models, and tactics attributed to guests (e.g., Brian Chesky's *Founder Mode*, Elena Verna's *Product-Led Sales triggers*, Shreyas Doshi's *LNO framework*).
5. **Actionable Implementation Checklist:** End with a 5-step operational framework.
