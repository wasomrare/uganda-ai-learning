"""Shared pytest fixtures for all tests."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def super_admin(db):
    return User.objects.create_superuser(
        username='superadmin_test',
        password='TestAdmin@123',
        first_name='Super',
        last_name='Admin',
        role='super_admin',
    )


@pytest.fixture
def teacher_user(db):
    return User.objects.create_user(
        username='teacher_test',
        password='TestTeacher@123',
        first_name='John',
        last_name='Teacher',
        role='teacher',
    )


@pytest.fixture
def student_user(db):
    return User.objects.create_user(
        username='student_test',
        password='TestStudent@123',
        first_name='Alice',
        last_name='Student',
        role='student',
    )


@pytest.fixture
def admin_client(api_client, super_admin):
    token = RefreshToken.for_user(super_admin)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    return api_client


@pytest.fixture
def teacher_client(api_client, teacher_user):
    token = RefreshToken.for_user(teacher_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    return api_client


@pytest.fixture
def student_client(api_client, student_user):
    token = RefreshToken.for_user(student_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
    return api_client


@pytest.fixture
def subject(db):
    from apps.subjects.models import Subject
    return Subject.objects.create(
        name='Mathematics',
        code='MTH',
        category='stem',
        class_levels=['P4', 'P5', 'P6', 'P7'],
        order=1,
    )


@pytest.fixture
def school_class(db):
    from apps.classes.models import SchoolClass
    from django.utils import timezone
    return SchoolClass.objects.create(
        name='P4 A',
        level='P4',
        stream='A',
        academic_year=timezone.now().year,
        term=1,
    )


@pytest.fixture
def topic(db, subject):
    from apps.curriculum.models import Topic
    return Topic.objects.create(
        subject=subject,
        class_level='P4',
        term=1,
        week=1,
        name='Whole Numbers',
        difficulty='easy',
        learning_objectives=['Count to 10,000'],
        key_vocabulary=['digit', 'place value'],
    )


@pytest.fixture
def mcq_question(db, subject, topic):
    from apps.question_bank.models import Question, MCQOption, QuestionAnswer
    question = Question.objects.create(
        question_type='mcq',
        subject=subject,
        topic=topic,
        class_level='P4',
        term=1,
        question_text='What is 2 + 2?',
        marks=1,
        difficulty='easy',
        source='teacher_created',
        is_approved=True,
    )
    MCQOption.objects.create(question=question, option_label='A', option_text='3', is_correct=False, order=0)
    MCQOption.objects.create(question=question, option_label='B', option_text='4', is_correct=True, order=1)
    MCQOption.objects.create(question=question, option_label='C', option_text='5', is_correct=False, order=2)
    MCQOption.objects.create(question=question, option_label='D', option_text='6', is_correct=False, order=3)
    QuestionAnswer.objects.create(
        question=question,
        answer_text='4',
        answer_keywords=['4', 'four'],
        explanation='2 plus 2 equals 4.',
        hints=['Count on your fingers'],
    )
    return question


@pytest.fixture
def student_profile(db, student_user, school_class):
    from apps.students.models import Student, StudentAIProfile
    student = Student.objects.create(
        user=student_user,
        admission_number='STU/2024/001',
        current_class=school_class,
        date_of_birth='2014-01-01',
        gender='F',
    )
    StudentAIProfile.objects.create(student=student)
    return student
