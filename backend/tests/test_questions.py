"""Question bank API tests."""
import pytest


@pytest.mark.django_db
class TestQuestionCRUD:
    def test_admin_can_create_question(self, admin_client, subject, topic):
        url = '/api/v1/questions/'
        payload = {
            'question_type': 'mcq',
            'subject': str(subject.id),
            'topic': str(topic.id),
            'class_level': 'P4',
            'term': 1,
            'question_text': 'What is the capital of Uganda?',
            'marks': 1,
            'difficulty': 'easy',
            'options': [
                {'option_label': 'A', 'option_text': 'Nairobi', 'is_correct': False, 'order': 0},
                {'option_label': 'B', 'option_text': 'Kampala', 'is_correct': True, 'order': 1},
                {'option_label': 'C', 'option_text': 'Kigali', 'is_correct': False, 'order': 2},
                {'option_label': 'D', 'option_text': 'Dar es Salaam', 'is_correct': False, 'order': 3},
            ],
            'answer': {
                'answer_text': 'Kampala',
                'answer_keywords': ['Kampala'],
                'explanation': 'Kampala is the capital city of Uganda.',
                'hints': ['It is also the largest city in Uganda.'],
                'marking_rubric': {},
                'minimum_keywords_required': 1,
            },
        }
        response = admin_client.post(url, payload, format='json')
        assert response.status_code == 201

    def test_teacher_can_view_questions(self, teacher_client, mcq_question):
        url = '/api/v1/questions/'
        response = teacher_client.get(url)
        assert response.status_code == 200

    def test_unauthenticated_cannot_view_questions(self, api_client):
        url = '/api/v1/questions/'
        response = api_client.get(url)
        assert response.status_code == 401

    def test_admin_can_approve_question(self, admin_client, mcq_question):
        url = f'/api/v1/questions/{mcq_question.id}/approve/'
        response = admin_client.post(url)
        assert response.status_code == 200
        mcq_question.refresh_from_db()
        assert mcq_question.is_approved is True

    def test_question_stats(self, admin_client, mcq_question):
        url = '/api/v1/questions/stats/'
        response = admin_client.get(url)
        assert response.status_code == 200
        assert 'total' in response.json().get('data', {})
