from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict, Any

class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider backend is reachable and configured."""
        pass

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3
    ) -> AsyncGenerator[str, None]:
        """Stream generated tokens from the model."""
        pass
