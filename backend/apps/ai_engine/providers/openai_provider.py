"""OpenAI provider — optional cloud fallback."""
import logging
from django.conf import settings
from .base import BaseAIProvider, AIResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """Optional cloud AI using OpenAI API (fallback when Ollama unavailable)."""

    def __init__(self):
        ai_settings = settings.AI_SETTINGS
        self.api_key = ai_settings.get('OPENAI_API_KEY', '')
        self.model = ai_settings.get('OPENAI_MODEL', 'gpt-4o-mini')
        self.timeout = ai_settings.get('TIMEOUT', 60)

    def get_model_name(self) -> str:
        return self.model

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate(self, prompt: str, system_prompt: str = '', temperature: float = 0.7, max_tokens: int = 2048) -> AIResponse:
        if not self.is_available():
            return AIResponse(content='', model=self.model, provider='openai', success=False, error='No API key')
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})

            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            return AIResponse(
                content=content,
                model=self.model,
                provider='openai',
                tokens_used=response.usage.total_tokens,
                success=True,
            )
        except Exception as e:
            logger.error('OpenAI error: %s', str(e))
            return AIResponse(content='', model=self.model, provider='openai', success=False, error=str(e))

    def generate_sync(self, prompt: str, system_prompt: str = '', temperature: float = 0.7, max_tokens: int = 2048) -> AIResponse:
        if not self.is_available():
            return AIResponse(content='', model=self.model, provider='openai', success=False, error='No API key')
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': prompt})

            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content
            return AIResponse(
                content=content,
                model=self.model,
                provider='openai',
                tokens_used=response.usage.total_tokens,
                success=True,
            )
        except Exception as e:
            logger.error('OpenAI sync error: %s', str(e))
            return AIResponse(content='', model=self.model, provider='openai', success=False, error=str(e))
