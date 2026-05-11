"""AI Engine service unit tests."""
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
class TestAIService:
    def test_ai_status_requires_auth(self, api_client):
        url = '/api/v1/ai/status/'
        response = api_client.get(url)
        assert response.status_code == 401

    def test_ai_status_for_admin(self, admin_client):
        url = '/api/v1/ai/status/'
        response = admin_client.get(url)
        assert response.status_code == 200
        data = response.json().get('data', {})
        assert 'ollama' in data
        assert 'primary_provider' in data

    @patch('apps.ai_engine.service.OllamaProvider.generate_sync')
    def test_generate_questions_returns_list(self, mock_generate, admin_client, subject, topic):
        from apps.ai_engine.providers.base import AIResponse
        mock_generate.return_value = AIResponse(
            content='[{"question_text": "What is 2+2?", "question_type": "mcq", "difficulty": "easy", "marks": 1, "estimated_time_seconds": 30, "options": [{"label": "A", "text": "3", "is_correct": false}, {"label": "B", "text": "4", "is_correct": true}], "answer": {"text": "4", "keywords": ["4"], "explanation": "2+2=4", "hints": []}, "learning_objective": "Basic addition"}]',
            model='llama3.2',
            provider='ollama',
            success=True,
        )
        url = '/api/v1/ai/generate/questions/'
        payload = {
            'class_level': 'P4',
            'subject_name': 'Mathematics',
            'topic_name': 'Addition',
            'question_type': 'mcq',
            'count': 1,
            'save_to_bank': False,
        }
        response = admin_client.post(url, payload, format='json')
        assert response.status_code == 200
        data = response.json().get('data', {})
        assert 'questions' in data

    @patch('apps.ai_engine.service.OllamaProvider.generate_sync')
    def test_fallback_when_ollama_fails(self, mock_generate):
        from apps.ai_engine.providers.base import AIResponse
        mock_generate.return_value = AIResponse(
            content='', model='llama3.2', provider='ollama', success=False, error='timeout'
        )
        from apps.ai_engine.service import ai_service
        with patch.object(ai_service.openai, 'is_available', return_value=False):
            with patch.object(ai_service.gemini, 'is_available', return_value=False):
                response = ai_service.generate_sync('test prompt', use_cache=False)
                assert response.provider == 'fallback'


class TestPromptTemplates:
    def test_question_generation_prompt_has_required_fields(self):
        from apps.ai_engine.prompts import PromptTemplates
        prompt = PromptTemplates.QUESTION_GENERATION_USER.format(
            class_level='P4',
            subject='Mathematics',
            topic='Fractions',
            question_type='mcq',
            difficulty='medium',
            count=5,
            term=1,
        )
        assert 'P4' in prompt
        assert 'Mathematics' in prompt
        assert 'Fractions' in prompt

    def test_offline_fallback_returns_empty_list_for_questions(self):
        from apps.ai_engine.prompts import PromptTemplates
        result = PromptTemplates.get_offline_fallback('generate questions for P4')
        assert result == '[]'

    def test_offline_fallback_for_marking(self):
        from apps.ai_engine.prompts import PromptTemplates
        result = PromptTemplates.get_offline_fallback('mark and score this answer')
        assert 'score' in result
