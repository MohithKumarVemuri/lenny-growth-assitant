import json
import logging
import httpx
from typing import AsyncGenerator, List, Dict, Any
from app.providers.base import BaseLLMProvider
from app.config import settings

logger = logging.getLogger(__name__)

class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL

    @property
    def name(self) -> str:
        return f"ollama ({self.model})"

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def get_models(self) -> List[str]:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    return [m.get("name") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "stream": True,
            "options": {"temperature": temperature}
        }

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as response:
                    if response.status_code != 200:
                        err_text = await response.aread()
                        logger.error(f"Ollama error {response.status_code}: {err_text.decode('utf-8', errors='ignore')}")
                        yield f"\n[Ollama Error: Service returned status {response.status_code}. Is model '{self.model}' pulled? Run: `ollama run {self.model}`]\n"
                        return

                    async for line in response.aiter_lines():
                        if line:
                            try:
                                chunk = json.loads(line)
                                token = chunk.get("message", {}).get("content", "")
                                if token:
                                    yield token
                                if chunk.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue

        except httpx.ConnectError:
            logger.warning(f"Cannot connect to Ollama at {self.base_url}.")
            # Provide actionable diagnostic
            yield (
                f"\n> **Note: Local Ollama service is not currently detected on `{self.base_url}`.**\n\n"
                f"To run with local models:\n"
                f"1. Start Ollama: `ollama serve`\n"
                f"2. Pull the model: `ollama pull {self.model}`\n\n"
                f"*Alternatively, you can switch provider to **Claude 3.5 Sonnet** or **GPT-4o** in the top-right model selector or configure API keys in `.env`.*\n\n"
            )
        except Exception as e:
            logger.error(f"Unexpected error in Ollama streaming: {e}")
            yield f"\n[Provider error: {str(e)}]\n"
