import json
import logging
import httpx
from typing import AsyncGenerator, List, Dict, Any
from app.providers.base import BaseLLMProvider
from app.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_COMPLETIONS_URL = "https://openrouter.ai/api/v1/chat/completions"

OPENROUTER_FREE_FALLBACK = "nex-agi/nex-n2.5-mini:free"

class ClaudeProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.ANTHROPIC_MODEL

    @property
    def name(self) -> str:
        return f"anthropic ({self.model})"

    async def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        if not await self.is_available():
            yield "\n> [Error: ANTHROPIC_API_KEY is not configured in `.env` or environment variables.]\n"
            return

        # Check if user provided an OpenRouter key (starts with sk-or-)
        if self.api_key.startswith("sk-or-"):
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://frontend-iota-nine-91.vercel.app",
                "X-Title": "Lenny Growth Assistant"
            }
            active_model = self.model
            if "/" not in active_model or active_model in ["claude-3-5-sonnet-20241022", "claude-3-5-sonnet"]:
                active_model = OPENROUTER_FREE_FALLBACK

            openrouter_messages = [{"role": "system", "content": system_prompt}] + messages
            payload = {
                "model": active_model,
                "messages": openrouter_messages,
                "temperature": temperature,
                "stream": True
            }

            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    async with client.stream(
                        "POST",
                        OPENROUTER_COMPLETIONS_URL,
                        headers=headers,
                        json=payload
                    ) as response:
                        if response.status_code in [400, 402, 404]:
                            logger.info(f"OpenRouter {response.status_code} for model {active_model}. Falling back to {OPENROUTER_FREE_FALLBACK}")
                            if active_model != OPENROUTER_FREE_FALLBACK:
                                yield f"> ℹ️ *Model `{active_model}` routed to free model `{OPENROUTER_FREE_FALLBACK}`:*\n\n"
                            payload["model"] = OPENROUTER_FREE_FALLBACK
                            async with client.stream("POST", OPENROUTER_COMPLETIONS_URL, headers=headers, json=payload) as fallback_resp:
                                if fallback_resp.status_code != 200:
                                    err_fb = (await fallback_resp.aread()).decode("utf-8", errors="ignore")
                                    yield f"\n[Free fallback model error ({fallback_resp.status_code}): {err_fb[:100]}]\n"
                                    return
                                async for line in fallback_resp.aiter_lines():
                                    if line.startswith("data: "):
                                        raw_data = line[6:].strip()
                                        if raw_data == "[DONE]":
                                            break
                                        try:
                                            data = json.loads(raw_data)
                                            choices = data.get("choices", [])
                                            if choices:
                                                delta = choices[0].get("delta", {})
                                                content = delta.get("content", "")
                                                if content:
                                                    yield content
                                        except json.JSONDecodeError:
                                            continue
                            return

                        elif response.status_code != 200:
                            err_text = (await response.aread()).decode("utf-8", errors="ignore")
                            logger.error(f"OpenRouter Claude error {response.status_code}: {err_text}")
                            yield f"\n[OpenRouter API error ({response.status_code}): {err_text[:120]}]\n"
                            return

                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                raw_data = line[6:].strip()
                                if raw_data == "[DONE]":
                                    break
                                try:
                                    data = json.loads(raw_data)
                                    choices = data.get("choices", [])
                                    if choices:
                                        delta = choices[0].get("delta", {})
                                        content = delta.get("content", "")
                                        if content:
                                            yield content
                                except json.JSONDecodeError:
                                    continue
            except Exception as e:
                logger.error(f"Error in OpenRouter Claude streaming: {e}")
                yield f"\n[OpenRouter provider error: {str(e)}]\n"
            return

        # Standard Anthropic Direct API
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        anthropic_messages = []
        for m in messages:
            anthropic_messages.append({"role": m["role"], "content": m["content"]})

        payload = {
            "model": self.model,
            "system": system_prompt,
            "messages": anthropic_messages,
            "max_tokens": 4096,
            "temperature": temperature,
            "stream": True
        }

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                async with client.stream(
                    "POST", 
                    "https://api.anthropic.com/v1/messages", 
                    headers=headers, 
                    json=payload
                ) as response:
                    if response.status_code != 200:
                        err_text = await response.aread()
                        logger.error(f"Anthropic error {response.status_code}: {err_text.decode('utf-8', errors='ignore')}")
                        yield f"\n[Anthropic API error ({response.status_code})]\n"
                        return

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            raw_data = line[6:].strip()
                            if raw_data == "[DONE]":
                                break
                            try:
                                data = json.loads(raw_data)
                                event_type = data.get("type")
                                if event_type == "content_block_delta":
                                    delta = data.get("delta", {})
                                    text = delta.get("text", "")
                                    if text:
                                        yield text
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            logger.error(f"Error in Claude streaming: {e}")
            yield f"\n[Anthropic provider error: {str(e)}]\n"


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL

    @property
    def name(self) -> str:
        return f"openai ({self.model})"

    async def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 10)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        if not await self.is_available():
            yield "\n> [Error: OPENAI_API_KEY is not configured in `.env` or environment variables.]\n"
            return

        is_openrouter = self.api_key.startswith("sk-or-")
        endpoint_url = OPENROUTER_COMPLETIONS_URL if is_openrouter else "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        if is_openrouter:
            headers["HTTP-Referer"] = "http://localhost:3000"
        active_model = self.model
        if is_openrouter and ("/" not in active_model or active_model in ["gpt-4o", "gpt-4"]):
            active_model = OPENROUTER_FREE_FALLBACK

        openai_messages = [{"role": "system", "content": system_prompt}] + messages
        payload = {
            "model": active_model,
            "messages": openai_messages,
            "temperature": temperature,
            "stream": True
        }

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                async with client.stream(
                    "POST",
                    endpoint_url,
                    headers=headers,
                    json=payload
                ) as response:
                    if is_openrouter and response.status_code in [400, 402, 404]:
                        # 400/402 Insufficient credits or invalid model -> fallback to free model
                        logger.info(f"OpenRouter {response.status_code} for model {active_model}. Falling back to {OPENROUTER_FREE_FALLBACK}")
                        if active_model != OPENROUTER_FREE_FALLBACK:
                            yield f"> ℹ️ *Model `{active_model}` routed to free model `{OPENROUTER_FREE_FALLBACK}`:*\n\n"
                        payload["model"] = OPENROUTER_FREE_FALLBACK
                        async with client.stream("POST", endpoint_url, headers=headers, json=payload) as fallback_resp:
                            if fallback_resp.status_code != 200:
                                err_fb = (await fallback_resp.aread()).decode("utf-8", errors="ignore")
                                yield f"\n[Free fallback model error ({fallback_resp.status_code}): {err_fb[:100]}]\n"
                                return
                            async for line in fallback_resp.aiter_lines():
                                if line.startswith("data: "):
                                    raw_data = line[6:].strip()
                                    if raw_data == "[DONE]":
                                        break
                                    try:
                                        data = json.loads(raw_data)
                                        choices = data.get("choices", [])
                                        if choices:
                                            delta = choices[0].get("delta", {})
                                            content = delta.get("content", "")
                                            if content:
                                                yield content
                                    except json.JSONDecodeError:
                                        continue
                        return

                    elif not is_openrouter and response.status_code == 429:
                        err_text = (await response.aread()).decode("utf-8", errors="ignore")
                        logger.error(f"OpenAI quota error: {err_text}")
                        yield (
                            f"\n> ⚠️ **OpenAI Credit Notice (429):** Your OpenAI key has $0 credits remaining (see [platform.openai.com/settings/organization/billing](https://platform.openai.com/settings/organization/billing/)).\n\n"
                            f"> *Displaying grounded answer from Lenny's podcast archive via Demo Simulation:*\n\n"
                        )
                        from app.providers.factory import DeterministicSimulationProvider
                        sim = DeterministicSimulationProvider()
                        async for token in sim.generate_response(messages, system_prompt, temperature):
                            yield token
                        return

                    elif response.status_code != 200:
                        err_text = (await response.aread()).decode("utf-8", errors="ignore")
                        logger.error(f"OpenAI/OpenRouter error {response.status_code}: {err_text}")
                        yield f"\n[Provider API error ({response.status_code}): {err_text[:120]}]\n"
                        return

                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            raw_data = line[6:].strip()
                            if raw_data == "[DONE]":
                                break
                            try:
                                data = json.loads(raw_data)
                                choices = data.get("choices", [])
                                if choices:
                                    delta = choices[0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            logger.error(f"Error in OpenAI streaming: {e}")
            yield f"\n[OpenAI provider error: {str(e)}]\n"

