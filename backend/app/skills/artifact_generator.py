import re
from typing import Optional, Dict, Any

ARTIFACT_SYSTEM_INSTRUCTIONS = """
When the user asks you to create an interactive tool, code widget, calculator, dashboard, launch checklist, product specification, or rich document, generate an Artifact.

Wrap the artifact using this exact container syntax:
<artifact type="html" title="Brief Descriptive Title">
...complete self-contained HTML/CSS/JS snippet...
</artifact>

Or for markdown documents:
<artifact type="markdown" title="Brief Descriptive Title">
# Document Title
...formatted markdown content...
</artifact>

Guidelines for HTML artifacts:
- Make them visually polished, responsive, and styled with modern CSS.
- Include self-contained inline CSS or system fonts (e.g. system-ui, -apple-system).
- Add interactive JavaScript where relevant (e.g., input sliders, recalculations, interactive check-boxes).
- Always ensure HTML is complete with `<!DOCTYPE html><html>...</html>`.
"""

def extract_artifact(text: str) -> Optional[Dict[str, Any]]:
    r"""
    Extracts artifact metadata and content from the response text if present.
    Pattern: <artifact type="(html|markdown)" title="([^"]+)">([\s\S]*?)</artifact>
    """
    pattern = r'<artifact\s+type="([^"]+)"\s+title="([^"]+)">([\s\S]*?)</artifact>'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return {
            "type": match.group(1).lower().strip(),
            "title": match.group(2).strip(),
            "content": match.group(3).strip()
        }
    return None

def strip_artifact_tags(text: str) -> str:
    """Removes raw artifact block from conversational text for clean reading."""
    pattern = r'<artifact\s+type="[^"]+"\s+title="[^"]+">[\s\S]*?</artifact>'
    cleaned = re.sub(pattern, "\n\n*(Artifact generated and displayed in canvas)*\n\n", text)
    return cleaned.strip()
