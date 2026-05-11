"""Student API tests."""
import pytest


@pytest.mark.django_db
class TestStudentCreation:
    def test_admin_can_create_student(self, admin_client, school_class):
        url = '/api/v1/students/'
        payload = {
            'first_name': 'Bob',
            'last_name': 'Mugisha',
            'username': 'bob_mugisha',
            'date_of_birth': '2014-03-15',
            'gender': 'M',
            'class_id': str(school_class.id),
        }
        response = admin_client.post(url, payload, format='json')
        assert response.status_code == 201
        data = response.json()
        assert 'student' in data.get('data', {})
        assert data['data']['student']['user']['username'] == 'bob_mugisha'

    def test_teacher_cannot_create_student(self, teacher_client, school_class):
        url = '/api/v1/students/'
        payload = {
            'first_name': 'Jane',
            'last_name': 'Nakato',
            'username': 'jane_nakato',
            'date_of_birth': '2013-05-20',
            'gender': 'F',
            'class_id': str(school_class.id),
        }
        response = teacher_client.post(url, payload, format='json')
        assert response.status_code == 403

    def test_unauthenticated_cannot_create_student(self, api_client, school_class):
        url = '/api/v1/students/'
        response = api_client.post(url, {}, format='json')
        assert response.status_code == 401


@pytest.mark.django_db
class TestStudentProfile:
    def test_student_can_view_own_profile(self, student_client, student_profile):
        url = '/api/v1/students/my-profile/'
        response = student_client.get(url)
        assert response.status_code == 200

    def test_admin_can_list_students(self, admin_client, student_profile):
        url = '/api/v1/students/'
        response = admin_client.get(url)
        assert response.status_code == 200
        assert response.json()['data']['count'] >= 1

    def test_teacher_can_list_students(self, teacher_client, student_profile):
        url = '/api/v1/students/'
        response = teacher_client.get(url)
        assert response.status_code == 200
