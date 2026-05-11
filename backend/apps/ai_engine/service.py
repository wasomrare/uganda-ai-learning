"""
Central AI Service — orchestrates all AI providers with fallback chain.
Primary: Ollama (local, free)
Fallback 1: OpenAI
Fallback 2: Gemini
Fallback 3: Template-based offline responses
"""
import json
import logging
import hashlib
from typing import Optional
from django.conf import settings
from django.core.cache import cache

from .providers.ollama_provider import OllamaProvider
from .providers.openai_provider import OpenAIProvider
from .providers.gemini_provider import GeminiProvider
from .providers.base import AIResponse
from .prompts import PromptTemplates

logger = logging.getLogger(__name__)


class AIService:
    """Central AI service with provider fallback chain."""

    def __init__(self):
        self.ollama = OllamaProvider()
        self.openai = OpenAIProvider()
        self.gemini = GeminiProvider()
        self.ai_settings = settings.AI_SETTINGS
        self.primary = self.ai_settings.get('PRIMARY_PROVIDER', 'ollama')
        self.fallback = self.ai_settings.get('FALLBACK_PROVIDER', 'openai')

    def _get_cache_key(self, prompt: str, system: str, model: str) -> str:
        content = f'{model}:{system}:{prompt}'
        return f'ai_cache:{hashlib.md5(content.encode()).hexdigest()}'

    def _get_from_cache(self, cache_key: str) -> Optional[AIResponse]:
        if not self.ai_settings.get('CACHE_AI_RESPONSES', True):
            return None
        cached = cache.get(cache_key)
        if cached:
            return AIResponse(**{**cached, 'cached': True})
        return None

    def _set_cache(self, cache_key: str, response: AIResponse):
        if not self.ai_settings.get('CACHE_AI_RESPONSES', True):
            return
        timeout = self.ai_settings.get('AI_CACHE_TIMEOUT', 3600)
        cache.set(cache_key, {
            'content': response.content,
            'model': response.model,
            'provider': response.provider,
            'tokens_used': response.tokens_used,
            'success': response.success,
        }, timeout)

    def generate_sync(
        self,
        prompt: str,
        system_prompt: str = '',
        temperature: float = 0.7,
        max_tokens: int = 2048,
        use_cache: bool = True,
    ) -> AIResponse:
        """Generate AI response synchronously with fallback chain."""

        cache_key = self._get_cache_key(prompt, system_prompt, self.primary)
        if use_cache:
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

        providers_to_try = self._get_provider_chain()

        for provider_name, provider in providers_to_try:
            if not provider.is_available():
                logger.info('AI provider %s not available, skipping.', provider_name)
                continue
            try:
                response = provider.generate_sync(prompt, system_prompt, temperature, max_tokens)
                if response.success and response.content:
                    if use_cache:
                        self._set_cache(cache_key, response)
                    logger.info('AI response from %s (%s)', provider_name, response.model)
                    return response
                logger.warning('AI provider %s returned empty/failed response.', provider_name)
            except Exception as e:
                logger.error('AI provider %s raised exception: %s', provider_name, str(e))
                continue

        logger.error('All AI providers failed. Using template fallback.')
        return self._fallback_response(prompt)

    def _get_provider_chain(self) -> list:
        chain = []
        provider_map = {
            'ollama': ('ollama', self.ollama),
            'openai': ('openai', self.openai),
            'gemini': ('gemini', self.gemini),
        }
        primary = provider_map.get(self.primary)
        if primary:
            chain.append(primary)
        for name, provider in provider_map.items():
            if name != self.primary:
                chain.append(provider)
        return chain

    def _fallback_response(self, prompt: str) -> AIResponse:
        """Template-based fallback when all AI providers are unavailable."""
        return AIResponse(
            content=PromptTemplates.get_offline_fallback(prompt),
            model='template_fallback',
            provider='fallback',
            success=True,
        )

    def generate_questions_sync(
        self,
        class_level: str,
        subject_name: str,
        topic_name: str,
        question_type: str = 'mcq',
        difficulty: str = 'medium',
        count: int = 5,
        term: int = 1,
    ) -> list:
        """Generate a batch of questions for a topic."""
        system_prompt = PromptTemplates.QUESTION_GENERATION_SYSTEM.format(
            class_level=class_level,
        )
        prompt = PromptTemplates.QUESTION_GENERATION_USER.format(
            class_level=class_level,
            subject=subject_name,
            topic=topic_name,
            question_type=question_type,
            difficulty=difficulty,
            count=count,
            term=term,
        )

        response = self.generate_sync(prompt, system_prompt, temperature=0.8, max_tokens=4096)
        if not response.success:
            return []

        return self._parse_questions_json(response.content, question_type)

    def grade_short_answer_sync(
        self,
        question_text: str,
        model_answer: str,
        keywords: list,
        student_answer: str,
        max_marks: float,
        class_level: str,
    ) -> dict:
        """AI-grade a short answer response."""
        system_prompt = PromptTemplates.MARKING_SYSTEM
        prompt = PromptTemplates.MARKING_SHORT_ANSWER.format(
            question=question_text,
            model_answer=model_answer,
            keywords=', '.join(keywords),
            student_answer=student_answer,
            max_marks=max_marks,
            class_level=class_level,
        )

        response = self.generate_sync(prompt, system_prompt, temperature=0.2, max_tokens=512)
        if not response.success:
            return {'score': 0, 'feedback': 'Marking unavailable.', 'confidence': 0}

        return self._parse_marking_result(response.content, max_marks)

    def grade_composition_sync(
        self,
        prompt_text: str,
        student_response: str,
        max_marks: float,
        class_level: str,
        rubric: dict,
    ) -> dict:
        """AI-grade a composition/essay."""
        system_prompt = PromptTemplates.COMPOSITION_MARKING_SYSTEM
        prompt = PromptTemplates.COMPOSITION_MARKING.format(
            composition_prompt=prompt_text,
            student_response=student_response,
            max_marks=max_marks,
            class_level=class_level,
            rubric=json.dumps(rubric),
        )

        response = self.generate_sync(prompt, system_prompt, temperature=0.2, max_tokens=1024)
        if not response.success:
            return {'score': 0, 'feedback': 'Marking unavailable.', 'breakdown': {}}

        return self._parse_composition_result(response.content, max_marks)

    def generate_explanation_sync(self, question_text: str, correct_answer: str, class_level: str) -> str:
        """Generate student-friendly explanation for a question."""
        prompt = PromptTemplates.EXPLANATION.format(
            question=question_text,
            answer=correct_answer,
            class_level=class_level,
        )
        response = self.generate_sync(prompt, temperature=0.5, max_tokens=512)
        return response.content if response.success else 'Explanation not available.'

    def generate_holiday_plan_sync(self, student_profile: dict, class_level: str, subjects: list, days: int) -> dict:
        """Generate a personalised holiday revision plan."""
        system_prompt = PromptTemplates.HOLIDAY_PLAN_SYSTEM
        prompt = PromptTemplates.HOLIDAY_PLAN.format(
            class_level=class_level,
            subjects=', '.join(subjects),
            weak_topics=', '.join(student_profile.get('weak_topics', [])),
            strong_topics=', '.join(student_profile.get('strong_topics', [])),
            days=days,
        )
        response = self.generate_sync(prompt, system_prompt, temperature=0.7, max_tokens=2048)
        if not response.success:
            return {'plan': [], 'error': 'Could not generate plan.'}
        return self._parse_holiday_plan(response.content)

    def generate_recommendations_sync(self, student_profile: dict, recent_performance: list) -> list:
        """Generate personalised learning recommendations."""
        prompt = PromptTemplates.RECOMMENDATIONS.format(
            class_level=student_profile.get('class_level', 'P4'),
            weak_subjects=', '.join(student_profile.get('weak_subjects', [])),
            weak_topics=', '.join(student_profile.get('weak_topics', [])),
            accuracy=student_profile.get('accuracy_rate', 0),
            streak=student_profile.get('current_streak', 0),
            recent_scores=json.dumps(recent_performance[-5:] if recent_performance else []),
        )
        response = self.generate_sync(prompt, temperature=0.6, max_tokens=1024)
        return self._parse_recommendations(response.content) if response.success else []

    def _parse_questions_json(self, content: str, question_type: str) -> list:
        """Parse AI-generated questions from JSON response."""
        try:
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
        except (json.JSONDecodeError, ValueError):
            pass
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                data = json.loads(content[start:end])
                if 'questions' in data:
                    return data['questions']
        except (json.JSONDecodeError, ValueError):
            pass
        return []

    def _parse_marking_result(self, content: str, max_marks: float) -> dict:
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                data = json.loads(content[start:end])
                score = min(float(data.get('score', 0)), max_marks)
                return {
                    'score': score,
                    'feedback': data.get('feedback', ''),
                    'confidence': data.get('confidence', 0.8),
                }
        except Exception:
            pass
        score = max_marks * 0.5
        return {'score': score, 'feedback': content[:200], 'confidence': 0.3}

    def _parse_composition_result(self, content: str, max_marks: float) -> dict:
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                data = json.loads(content[start:end])
                return {
                    'score': min(float(data.get('total_score', 0)), max_marks),
                    'feedback': data.get('overall_feedback', ''),
                    'breakdown': data.get('breakdown', {}),
                    'suggestions': data.get('suggestions', []),
                }
        except Exception:
            pass
        return {'score': 0, 'feedback': content[:300], 'breakdown': {}}

    def _parse_holiday_plan(self, content: str) -> dict:
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
        except Exception:
            pass
        return {'plan': [], 'raw': content}

    def _parse_recommendations(self, content: str) -> list:
        try:
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
        except Exception:
            pass
        return [{'type': 'general', 'message': content[:200]}]


ai_service = AIService()
