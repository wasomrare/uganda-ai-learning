"""Ollama local AI provider — primary free AI engine."""
import logging
import httpx
from django.conf import settings
from .base import BaseAIProvider, AIResponse

logger = logging.getLogger(__name__)


class OllamaProvider(BaseAIProvider):
    """Primary AI provider using Ollama with local models (DeepSeek, Llama3, Mistral)."""

    def __init__(self):
        ai_settings = settings.AI_SETTINGS
        self.base_url = ai_settings.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        self.default_model = ai_settings.get('OLLAMA_DEFAULT_MODEL', 'llama3.2')
        self.timeout = ai_settings.get('TIMEOUT', 60)

    def get_model_name(self) -> str:
        return self.default_model

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=5) as client:
                resp = client.get(f'{self.base_url}/api/tags')
                return resp.status_code == 200
        except Exception:
            return False

    async def generate(
        self,
        prompt: str,
        system_prompt: str = '',
        temperature: float = 0.7,
        max_tokens: int = 2048,
        model: str = None,
    ) -> AIResponse:
        model_to_use = model or self.default_model
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        payload = {
            'model': model_to_use,
            'messages': messages,
            'stream': False,
            'options': {
                'temperature': temperature,
                'num_predict': max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f'{self.base_url}/api/chat',
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                content = data.get('message', {}).get('content', '')
                return AIResponse(
                    content=content,
                    model=model_to_use,
                    provider='ollama',
                    tokens_used=data.get('eval_count', 0),
                    success=True,
                )
        except httpx.TimeoutException:
            logger.error('Ollama request timed out for model %s', model_to_use)
            return AIResponse(content='', model=model_to_use, provider='ollama', success=False, error='timeout')
        except Exception as e:
            logger.error('Ollama error: %s', str(e))
            return AIResponse(content='', model=model_to_use, provider='ollama', success=False, error=str(e))

    def generate_sync(
        self,
        prompt: str,
        system_prompt: str = '',
        temperature: float = 0.7,
        max_tokens: int = 2048,
        model: str = None,
    ) -> AIResponse:
        """Synchronous version for Celery tasks."""
        model_to_use = model or self.default_model
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        payload = {
            'model': model_to_use,
            'messages': messages,
            'stream': False,
            'options': {
                'temperature': temperature,
                'num_predict': max_tokens,
            },
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f'{self.base_url}/api/chat', json=payload)
                response.raise_for_status()
                data = response.json()
                content = data.get('message', {}).get('content', '')
                return AIResponse(
                    content=content,
                    model=model_to_use,
                    provider='ollama',
                    tokens_used=data.get('eval_count', 0),
                    success=True,
                )
        except Exception as e:
            logger.error('Ollama sync error: %s', str(e))
            return AIResponse(content='', model=model_to_use, provider='ollama', success=False, error=str(e))
