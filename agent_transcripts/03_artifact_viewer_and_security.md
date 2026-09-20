# Agent Transcript 03: Claude-Style Artifact Viewer & Isolation Security

**Date:** 2026-09-18  
**Author / Agent:** Antigravity Coding Agent  
**Focus Area:** Sandboxed Iframe Security, DOMPurify, Artifact Tag Extraction, and Split-Pane UX

---

## 1. Challenge: Safe Execution of Untrusted AI-Generated HTML/JS

The core requirement demands that the assistant can generate complete HTML/CSS snippets (e.g. interactive retention calculators, launch checklists, scoring rubrics) and render them directly inside the web product without redirecting to an external application or displaying only raw code.

### Security Vulnerabilities Analyzed:
1. **Host DOM Hijacking:** An unisolated script could read the parent window DOM, access input fields, or insert phishing elements.
2. **Session Theft:** An unisolated script could read `localStorage` containing API keys or cookies.
3. **Host Navigation Hijack:** An unisolated script could invoke `window.top.location = 'https://malicious-site.com'`.

---

## 2. The Defense-in-Depth Solution

We implemented a two-stage containment strategy:

### Stage 1: DOMPurify Sanitization
Before the HTML string is passed into the DOM or iframe `srcdoc`, it is pre-sanitized with DOMPurify:
```typescript
const cleanHtml = DOMPurify.sanitize(rawHtml, {
  WHOLE_DOCUMENT: true,
  ADD_TAGS: ['style', 'link', 'script'],
  ADD_ATTR: ['target', 'id', 'class', 'style', 'onclick']
});
```

### Stage 2: Strict Iframe Sandboxing
We mounted the sanitized HTML inside a dedicated `<iframe>`:
```tsx
<iframe
  title={title}
  srcDoc={cleanHtml}
  sandbox="allow-scripts"
  className="w-full h-full border-none"
/>
```

**Why this configuration is optimal:**
- `sandbox="allow-scripts"` allows calculators and interactive widgets to function (sliders, event listeners, local recalculations).
- **CRITICAL OMISSION of `allow-same-origin`:** Treats the document inside the iframe as having an opaque, unique origin (`null`). Even if a script executes inside the iframe, the browser prevents it from accessing `window.parent`, parent cookies, or host `localStorage`.
- **CRITICAL OMISSION of `allow-top-navigation`:** Prevents scripts from redirecting the parent window.

---

## 3. UI/UX Dual-Pane Implementation

- Integrated tabbed navigation: **Live Preview** (rendered sandboxed container) vs. **Raw Code** (syntax highlighted).
- Added one-click clipboard copy and direct download (`.html` or `.md`) buttons.
- Responsive layout: On desktop screens ($\ge 1024\text{px}$), the chat and artifact viewer coexist side-by-side (50/50 split), mirroring the Claude Artifacts experience.
