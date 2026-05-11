"""Base AI provider interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class AIResponse:
    content: str
    model: str
    provider: str
    tokens_used: int = 0
    success: bool = True
    error: Optional[str] = None
    cached: bool = False


class BaseAIProvider(ABC):
    """Abstract base for all AI providers."""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = '', temperature: float = 0.7, max_tokens: int = 2048) -> AIResponse:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        pass
