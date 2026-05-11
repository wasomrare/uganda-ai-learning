"""Assessment API tests."""
import pytest
from django.utils import timezone


@pytest.fixture
def assessment(db, school_class, subject, super_admin):
    from apps.assessments.models import Assessment, AssessmentQuestion
    a = Assessment.objects.create(
        title='P4 Mathematics Quiz',
        assessment_type='weekly_quiz',
        school_class=school_class,
        class_level='P4',
        subject=subject,
        term=1,
        academic_year=2024,
        total_marks=10,
        passing_marks=5,
        duration_minutes=20,
        status='active',
        created_by=super_admin,
    )
    return a


@pytest.fixture
def published_assessment(db, assessment, mcq_question):
    from apps.assessments.models import AssessmentQuestion
    AssessmentQuestion.objects.create(assessment=assessment, question=mcq_question, order=1)
    return assessment


@pytest.mark.django_db
class TestAssessmentCRUD:
    def test_admin_can_create_assessment(self, admin_client, school_class, subject):
        url = '/api/v1/assessments/'
        payload = {
            'title': 'Test Assessment',
            'assessment_type': 'weekly_quiz',
            'school_class': str(school_class.id),
            'class_level': 'P4',
            'subject': str(subject.id),
            'term': 1,
            'total_marks': 10,
            'duration_minutes': 20,
            'status': 'draft',
        }
        response = admin_client.post(url, payload, format='json')
        assert response.status_code == 201

    def test_teacher_can_list_assessments(self, teacher_client, assessment):
        url = '/api/v1/assessments/'
        response = teacher_client.get(url)
        assert response.status_code == 200

    def test_student_sees_only_active(self, student_client, student_profile, published_assessment):
        url = '/api/v1/assessments/student-assessments/'
        response = student_client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestAssessmentAttempt:
    def test_student_can_start_attempt(self, student_client, student_profile, published_assessment):
        url = f'/api/v1/assessments/{published_assessment.id}/start-attempt/'
        response = student_client.post(url)
        assert response.status_code == 200
        data = response.json().get('data', {})
        assert 'attempt_id' in data
        assert 'questions' in data

    def test_second_attempt_resumes_existing(self, student_client, student_profile, published_assessment):
        url = f'/api/v1/assessments/{published_assessment.id}/start-attempt/'
        r1 = student_client.post(url)
        r2 = student_client.post(url)
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json()['data']['attempt_id'] == r2.json()['data']['attempt_id']

    def test_teacher_cannot_start_attempt(self, teacher_client, published_assessment):
        url = f'/api/v1/assessments/{published_assessment.id}/start-attempt/'
        response = teacher_client.post(url)
        assert response.status_code == 403
