"""Gemini provider — optional cloud fallback."""
import logging
from django.conf import settings
from .base import BaseAIProvider, AIResponse

logger = logging.getLogger(__name__)


class GeminiProvider(BaseAIProvider):
    """Optional Google Gemini AI provider."""

    def __init__(self):
        ai_settings = settings.AI_SETTINGS
        self.api_key = ai_settings.get('GEMINI_API_KEY', '')
        self.model = ai_settings.get('GEMINI_MODEL', 'gemini-1.5-flash')

    def get_model_name(self) -> str:
        return self.model

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate(self, prompt: str, system_prompt: str = '', temperature: float = 0.7, max_tokens: int = 2048) -> AIResponse:
        if not self.is_available():
            return AIResponse(content='', model=self.model, provider='gemini', success=False, error='No API key')
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            full_prompt = f'{system_prompt}\n\n{prompt}' if system_prompt else prompt
            response = model.generate_content(full_prompt)
            return AIResponse(
                content=response.text,
                model=self.model,
                provider='gemini',
                success=True,
            )
        except Exception as e:
            logger.error('Gemini error: %s', str(e))
            return AIResponse(content='', model=self.model, provider='gemini', success=False, error=str(e))

    def generate_sync(self, prompt: str, system_prompt: str = '', temperature: float = 0.7, max_tokens: int = 2048) -> AIResponse:
        if not self.is_available():
            return AIResponse(content='', model=self.model, provider='gemini', success=False, error='No API key')
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            full_prompt = f'{system_prompt}\n\n{prompt}' if system_prompt else prompt
            response = model.generate_content(full_prompt)
            return AIResponse(content=response.text, model=self.model, provider='gemini', success=True)
        except Exception as e:
            logger.error('Gemini sync error: %s', str(e))
            return AIResponse(content='', model=self.model, provider='gemini', success=False, error=str(e))
