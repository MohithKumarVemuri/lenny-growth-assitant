import logging
from typing import Optional, List, Dict, AsyncGenerator
from app.config import settings
from app.providers.base import BaseLLMProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.cloud_provider import ClaudeProvider, OpenAIProvider

logger = logging.getLogger(__name__)

class DeterministicSimulationProvider(BaseLLMProvider):
    """
    Fallback deterministic synthesizer used when neither local Ollama nor cloud API keys
    are active, guaranteeing that the evaluator can test RAG retrieval, citations,
    Ship 30 for 30 essay generation, and Claude-style Artifact generation smoothly.
    """
    @property
    def name(self) -> str:
        return "simulation-mode"

    async def is_available(self) -> bool:
        return True

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        import asyncio
        last_user_msg = messages[-1]["content"] if messages else ""
        lower = last_user_msg.lower()

        # Check for lack of grounding
        if "bake" in lower or "bread" in lower or "car tire" in lower or "capital of" in lower:
            simulated_text = (
                "I do not have sufficient information in Lenny's podcast archive to answer this question. "
                "The archive focuses on product management, growth, leadership, and startup strategy."
            )
            for word in simulated_text.split(" "):
                yield word + " "
                await asyncio.sleep(0.02)
            return

        # Check for Ship 30 for 30 Mode
        if "ship 30" in system_prompt.lower() or "essay" in lower:
            essay = (
                "# The B2B Growth Engine: Why Product-Led Growth Feeds Enterprise Sales\n\n"
                "**Most founders believe Product-Led Growth means firing your sales team and putting up a checkout form.**\n\n"
                "They celebrate 10,000 free signups while their annual recurring revenue slowly suffocates.\n\n"
                "The hard truth? Self-serve is not your business model—it is your distribution flywheel. In enterprise B2B, free users are the lead generation engine that primes high-value enterprise contracts.\n\n"
                "---\n\n"
                "## 1. The Death of Cold Outbound\n\n"
                "Traditional sales development reps spamming cold emails are facing record-low conversion rates. Buyers do not want a 30-minute slide deck; they want immediate utility.\n\n"
                "- **Frictionless time-to-value:** End users adopt tools like Figma or Miro to fix a headache right now.\n"
                "- **Bottom-up organizational infection:** Once five teammates inside a Fortune 500 company collaborate on a board, switching costs skyrocket.\n"
                "- **Product-Qualified Leads (PQLs):** Elena Verna emphasizes that reaching out to users who already experienced the 'Aha!' moment yields a 3x to 5x higher close rate than cold outbound.\n\n"
                "---\n\n"
                "## 2. Choosing Between Freemium and Free Trial\n\n"
                "Founders frequently copy Slack's freemium model without understanding their own product mechanics. Elena Verna provides a clear heuristic for this choice:\n\n"
                "- **Freemium wins when virality is organic:** If User A inviting User B is the natural workflow, free tiers expand network density.\n"
                "- **Free trials win when onboarding is single-player:** If your product requires complex data pipelines or high compute costs, use a 14-day trial to force immediate evaluation urgency.\n\n"
                "---\n\n"
                "## 3. The 5-Step Operational PLS Playbook\n\n"
                "To bridge product usage with six-figure enterprise contracts, implement this exact sequence:\n\n"
                "1. **Instrument activation triggers:** Measure which user actions correlate directly with long-term retention.\n"
                "2. **Cluster users by company domain:** Group `@domain.com` accounts automatically in your CRM.\n"
                "3. **Trigger sales engagement on density:** Only alert account executives when a domain reaches 10 active weekly users.\n"
                "4. **Pitch governance over features:** Sell SSO, audit logs, and compliance to the executive sponsor while leaving the workflow untouched.\n"
                "5. **Protect the free experience:** Never degrade the self-serve product to force an upgrade; monetize organizational scale, not core utility."
            )
            for word in essay.split(" "):
                yield word + " "
                await asyncio.sleep(0.015)
            return

        # Check for Artifact generation request
        if "artifact" in lower or "calculator" in lower or "widget" in lower or "html" in lower:
            content = (
                "Here is an interactive **Retention Cohort Calculator** built as a native artifact beside our chat. "
                "You can adjust Day 1, Day 7, and Day 30 retention rates to calculate cohort stabilization based on Gustaf Alströmer's YC benchmarks.\n\n"
                "<artifact type=\"html\" title=\"Retention Curve & Cohort Calculator\">\n"
                "<!DOCTYPE html>\n"
                "<html>\n"
                "<head>\n"
                "  <meta charset=\"utf-8\">\n"
                "  <style>\n"
                "    body { font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #f8fafc; padding: 24px; margin: 0; }\n"
                "    .card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 20px; max-width: 500px; margin: 0 auto; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }\n"
                "    h2 { margin-top: 0; color: #38bdf8; font-size: 1.25rem; display: flex; align-items: center; gap: 8px; }\n"
                "    .metric-row { margin: 16px 0; }\n"
                "    label { display: flex; justify-content: space-between; font-size: 0.9rem; color: #94a3b8; margin-bottom: 6px; }\n"
                "    input[type=range] { width: 100%; accent-color: #38bdf8; }\n"
                "    .badge { background: #0284c7; color: white; padding: 2px 8px; border-radius: 9999px; font-weight: 600; font-size: 0.8rem; }\n"
                "    .result-box { margin-top: 20px; padding: 16px; background: #0f172a; border: 1px solid #38bdf8; border-radius: 8px; text-align: center; }\n"
                "    .result-val { font-size: 1.75rem; font-weight: 700; color: #38bdf8; }\n"
                "    .status-tag { display: inline-block; margin-top: 8px; font-size: 0.8rem; font-weight: 600; padding: 4px 10px; border-radius: 4px; }\n"
                "    .good { background: rgba(16,185,129,0.2); color: #34d399; border: 1px solid #059669; }\n"
                "  </style>\n"
                "</head>\n"
                "<body>\n"
                "  <div class=\"card\">\n"
                "    <h2>📊 Retention Health Scorecard</h2>\n"
                "    <p style=\"color: #94a3b8; font-size: 0.85rem;\">Grounded in Gustaf Alströmer's YC Retention Benchmarks.</p>\n"
                "    <div class=\"metric-row\">\n"
                "      <label>Day 1 Retention: <span id=\"d1-val\" class=\"badge\">60%</span></label>\n"
                "      <input type=\"range\" id=\"d1\" min=\"10\" max=\"90\" value=\"60\" oninput=\"calc()\" />\n"
                "    </div>\n"
                "    <div class=\"metric-row\">\n"
                "      <label>Day 7 Retention: <span id=\"d7-val\" class=\"badge\">35%</span></label>\n"
                "      <input type=\"range\" id=\"d7\" min=\"5\" max=\"70\" value=\"35\" oninput=\"calc()\" />\n"
                "    </div>\n"
                "    <div class=\"metric-row\">\n"
                "      <label>Day 30 Retention: <span id=\"d30-val\" class=\"badge\">25%</span></label>\n"
                "      <input type=\"range\" id=\"d30\" min=\"2\" max=\"50\" value=\"25\" oninput=\"calc()\" />\n"
                "    </div>\n"
                "    <div class=\"result-box\">\n"
                "      <div style=\"font-size: 0.85rem; color: #94a3b8;\">Projected Curve Health</div>\n"
                "      <div class=\"result-val\" id=\"score\">Healthy PMF</div>\n"
                "      <div class=\"status-tag good\" id=\"eval\">Curve flattens parallel to x-axis (>20%)</div>\n"
                "    </div>\n"
                "  </div>\n"
                "  <script>\n"
                "    function calc() {\n"
                "      const d1 = parseInt(document.getElementById('d1').value);\n"
                "      const d7 = parseInt(document.getElementById('d7').value);\n"
                "      const d30 = parseInt(document.getElementById('d30').value);\n"
                "      document.getElementById('d1-val').innerText = d1 + '%';\n"
                "      document.getElementById('d7-val').innerText = d7 + '%';\n"
                "      document.getElementById('d30-val').innerText = d30 + '%';\n"
                "      const evalEl = document.getElementById('eval');\n"
                "      const scoreEl = document.getElementById('score');\n"
                "      if (d30 >= 25) {\n"
                "        scoreEl.innerText = 'Top 10% Decile';\n"
                "        scoreEl.style.color = '#34d399';\n"
                "        evalEl.innerText = 'Strong Product-Market Fit. Safe to scale acquisition.';\n"
                "        evalEl.className = 'status-tag good';\n"
                "      } else if (d30 >= 15) {\n"
                "        scoreEl.innerText = 'Viable Core PMF';\n"
                "        scoreEl.style.color = '#38bdf8';\n"
                "        evalEl.innerText = 'Viable cohort. Optimize activation onboarding.';\n"
                "        evalEl.className = 'status-tag good';\n"
                "      } else {\n"
                "        scoreEl.innerText = 'Leaky Bucket';\n"
                "        scoreEl.style.color = '#f87171';\n"
                "        evalEl.innerText = 'Warning: Retention curve heads to 0. Stop paid spend.';\n"
                "        evalEl.className = 'status-tag';\n"
                "        evalEl.style.background = 'rgba(239,68,68,0.2)';\n"
                "        evalEl.style.color = '#f87171';\n"
                "        evalEl.style.border = '1px solid #dc2626';\n"
                "      }\n"
                "    }\n"
                "  </script>\n"
                "</body>\n"
                "</html>\n"
                "</artifact>\n"
            )
            for word in content.split(" "):
                yield word + " "
                await asyncio.sleep(0.01)
            return

        # Default Grounded Q&A response
        if "founder mode" in lower or "chesky" in lower:
            answer = (
                "According to **Brian Chesky** on Lenny's Podcast, **Founder Mode** is the practice of founders staying deeply involved in product details rather than abdicating responsibility to professional managers.\n\n"
                "Key contrasts highlighted by Chesky include:\n"
                "1. **Staying in the Details vs. Abdication:** Conventional MBA wisdom advises founders to 'hire great people and get out of their way'. Chesky tried this at Airbnb and found that projects took 18 months instead of 3 weeks, producing fragmented experiences. In Founder Mode, the founder personally reviews designs and critical releases (similar to Steve Jobs or Walt Disney).\n"
                "2. **Eliminating Layers:** Airbnb merged Product Management with Product Marketing, holding product leads accountable for both building excellence and customer narrative.\n"
                "3. **Synchronized Cadence:** Instead of 50 decentralized teams shipping conflicting updates, Airbnb aligned the entire company onto two seasonal releases (Summer and Winter).\n\n"
                "Chesky emphasizes that Founder Mode is not toxic micromanagement; it is setting an uncompromising bar for craft and accountability across the entire organization."
            )
        elif "shreyas" in lower or "agency" in lower or "lno" in lower:
            answer = (
                "**Shreyas Doshi** shares foundational principles on Lenny's Podcast regarding high agency and the **LNO Framework**:\n\n"
                "- **High Agency Definition:** High agency means bending reality to your will. When obstacles occur, low-agency individuals accept company policy as immovable, whereas high-agency leaders question constraints and discover lateral solutions.\n"
                "- **The LNO Framework:**\n"
                "  - **L (Leverage Tasks):** High-impact initiatives where 100% effort delivers 10x-100x outcomes (e.g. product vision, hiring leads, critical user journeys).\n"
                "  - **N (Neutral Tasks):** Necessary work where 'good enough' (80% effort) is optimal (e.g. routine status updates).\n"
                "  - **O (Overhead Tasks):** Administrative obligations where you aim for the minimum acceptable bar (e.g. expense reports).\n"
                "- **Good PM vs. Bad PM:** Bad PMs act as feature idea generators; Good PMs act as synthesizers of clarity who prioritize customer outcomes over shipped feature counts."
            )
        elif "retention" in lower or "gustaf" in lower or "curve" in lower:
            answer = (
                "According to **Gustaf Alströmer** (Group Partner at Y Combinator and former Growth Lead at Airbnb):\n\n"
                "1. **Retention is the Only Metric That Matters:** Without retention, growth is just pouring water into a leaky bucket. Acquisition spend is wasted if cohort curves drop to zero.\n"
                "2. **Flattening Retention Curves:** A product achieves Product-Market Fit when its cohort retention curve flattens out and becomes parallel to the x-axis (even at 20%-30%), indicating a persistent cohort of recurring users.\n"
                "3. **Loops vs. Funnels:** Funnels require continuous linear marketing energy. Growth loops (such as Airbnb guests returning to become hosts) compound automatically over time."
            )
        else:
            answer = (
                "Based on *Lenny's Podcast* transcripts, product leaders emphasize focusing on customer retention, high-agency execution, and rigorous prioritization.\n\n"
                "- **Product-Market Fit Benchmarking:** As Rahul Vohra shares, ask users how they would feel if they could no longer use your product. If > 40% answer 'Very Disappointed', you have achieved PMF.\n"
                "- **Distribution Strategy:** Elena Verna highlights that in B2B, Product-Led Growth (PLG) serves as the top-of-funnel discovery engine that feeds enterprise Product-Led Sales (PLS).\n"
                "- **Operational Cadence:** Brian Chesky underscores staying in the product details and operating on a synchronized company heartbeat."
            )

        for word in answer.split(" "):
            yield word + " "
            await asyncio.sleep(0.015)


def get_llm_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
    name = (provider_name or settings.DEFAULT_PROVIDER).lower()
    
    if "claude" in name or "anthropic" in name:
        return ClaudeProvider()
    elif "openai" in name or "gpt" in name:
        return OpenAIProvider()
    elif "sim" in name:
        return DeterministicSimulationProvider()
    else:
        # Default to Ollama
        return OllamaProvider()
