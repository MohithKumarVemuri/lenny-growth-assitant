# Design System & UI/UX Specification
## The Lenny Growth Assistant

---

## 1. Design Principles & Aesthetics

The Lenny Growth Assistant is designed around four core user experience pillars:
1. **Uncompromising Grounding & Transparency:** Never hide the origin of an insight. Every fact, statistic, and framework retrieved from *Lenny’s Podcast* displays an interactive citation badge linking directly to the guest, episode, and timestamp.
2. **Claude-Style Seamless Artifact Workspace:** Complex documents, interactive calculators, and prototypes must not pollute the conversational flow. They dynamically slide into an adjacent right-hand canvas, preserving conversational context while offering a dedicated review and interaction environment.
3. **Tactile Micro-Interactions & Real-Time Feedback:** Streaming tokens, glowing state badges, smooth drawer transitions, and responsive status indicators keep the user informed during RAG retrieval and inference.
4. **Restraint & High-Information Density:** Styled using a modern, refined dark/light slate palette with high-contrast typography, clear hierarchy, and clean whitespace tailored for product leaders who value clarity over clutter.

---

## 2. Information Architecture & Layout Hierarchy

The application features a responsive three-tier layout:

```
┌─────────────┬───────────────────────────────────────────┬────────────────────────────────────────┐
│   Sidebar   │                 Chat Pane                 │         Artifact Canvas Drawer         │
│  (260px)    │                  (Flex)                   │             (550px / 50%)              │
├─────────────┼───────────────────────────────────────────┼────────────────────────────────────────┤
│ • App Logo  │ Header:                                   │ Header:                                │
│ • + New Chat│  - Active Model Badge (Ollama/Claude/GPT) │  - Artifact Title & Type Tag           │
│ • Sessions  │  - Mode Selector (Default/Ship30/Artifact)│  - Preview / Code Tab Toggle           │
│   History   │  - System Health Indicator                │  - Copy Source & Download Actions      │
│ • Clear All ├───────────────────────────────────────────┼────────────────────────────────────────┤
│ • Status    │ Message Stream:                           │ Content:                               │
│             │  - User Prompt Bubble                     │  - [Tab 1: Preview]                    │
│             │  - Assistant Response (Markdown)          │    Sandboxed <iframe> (allow-scripts)  │
│             │  - Expandable Citation Cards              │    or Rendered Markdown                │
│             │  - "View Artifact" Card Trigger           │  - [Tab 2: Code]                       │
│             ├───────────────────────────────────────────┤    Prism Syntax Highlighted Code       │
│             │ Input Bar:                                │                                        │
│             │  - Quick Prompt Starter Pills             │                                        │
│             │  - Auto-growing Textarea & Send Button    │                                        │
└─────────────┴───────────────────────────────────────────┴────────────────────────────────────────┘
```

---

## 3. Design Tokens & Visual Hierarchy

### 3.1 Color Palette
- **Backgrounds:**
  - Dark Primary: `#0B0F17` (Deep Obsidian Slate)
  - Dark Secondary / Cards: `#131B2A` (Rich Navy Slate)
  - Dark Input / Elevate: `#1C2638` (Elevated Panel)
  - Border Accents: `#2A3850` (Subtle divider)
- **Brand Accents:**
  - Lenny Amber / Gold: `#F59E0B` (Accent glow, citation badges, key metrics)
  - Growth Emerald: `#10B981` (Online status, verified grounding)
  - Electric Indigo: `#6366F1` (Ship 30 for 30 mode & buttons)
  - Danger Rose: `#F43F5E` (Errors, delete warnings)
- **Typography Colors:**
  - Heading & Primary: `#F8FAFC` (Slate 50)
  - Body & Secondary: `#94A3B8` (Slate 400)
  - Muted / Timestamps: `#64748B` (Slate 500)

### 3.2 Typography Hierarchy
- **Font Stack:** Inter, system-ui, -apple-system, sans-serif for UI; JetBrains Mono or Fira Code for code blocks.
- **Headings:**
  - `H1`: 24px / 1.3 line-height / Semi-bold (App Title, Artifact Title)
  - `H2`: 18px / 1.4 line-height / Semi-bold (Essay Sections, Modal Headers)
  - `H3`: 15px / 1.4 line-height / Medium (Sub-sections, Citation headers)
  - `Body`: 14px / 1.5 line-height / Regular (Chat bubbles, explanations)
  - `Code / Meta`: 12px / 1.4 line-height / Regular (Tags, timestamps, code)

---

## 4. Key Interactive States & Transitions

### 4.1 Chat Streaming States
1. **Idle State:** Prompt starter pills available (e.g. *"What did Brian Chesky say about Founder Mode?"*, *"Generate a Ship 30 essay on Elena Verna's B2B PLG flywheel"*, *"Create an interactive retention calculator artifact"*).
2. **Retrieving Knowledge State:** Pulsing badge indicates *"Searching transcript embeddings..."* with elapsed timer.
3. **Token Streaming State:** Smooth cursor caret animation; citation source cards pop in immediately before token generation.
4. **Complete State:** Formatted markdown rendered, source cards expandable to inspect verbatim chunks, and artifact cards appear with an animated "Open in Canvas" button.

### 4.2 Artifact Viewer Drawer States
- **Closed / Hidden:** Main chat pane expands to full available width.
- **Open / Split:** Artifact drawer slides smoothly from the right (CSS transform `translateX` 200ms ease-out). On screens $< 1024\text{px}$, it switches to an overlay modal with full-screen toggle.
- **Tab Switching:** Instant transition between **Live Preview** (interactive sandboxed iframe) and **Raw Code** (with line numbers and one-click copy).

---

## 5. Accessibility (a11y) & Usability Considerations

- **Keyboard Navigation:** `Tab` order traverses sidebar, prompt starters, message input, and artifact action buttons. `Escape` key immediately closes the artifact drawer.
- **Focus Indicators:** Explicit ring outlines (`ring-2 ring-amber-500/50`) on all interactive buttons, inputs, and tabs.
- **Screen Reader Support:** Semantic HTML elements (`<main>`, `<aside>`, `<nav>`, `<article>`, `<header>`), `aria-live="polite"` on streaming response regions, and descriptive `aria-label` tags on icons.
- **Contrast Ratios:** All text combinations satisfy WCAG 2.1 AA minimum contrast ($\ge 4.5:1$ for body, $\ge 3:1$ for large text).
